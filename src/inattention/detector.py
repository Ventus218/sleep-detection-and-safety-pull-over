from .utils import EyeStateDetector, CameraStream
from threading import Lock, Thread
from typing import Optional
import logging
import queue
import numpy as np
import cv2


class InattentionDetector:
    """
    Detect whether the driver is inattentive (not focused on the road),
    based on eye state predictions from frames captured by a CameraStream.
    """

    def __init__(self, cam_stream: "CameraStream", eye_threshold: float = 0.15):
        """
        Parameters
        ----------
        cam_stream : CameraStream
            Source of images (grayscale frames are used for detection).
        eye_threshold : float
            Threshold parameter passed to EyeStateDetector (e.g., for
            determining if eyes are open or closed).
        """
        self.cam = cam_stream
        self.detector = EyeStateDetector(eye_threshold)

        self._queue: queue.Queue = queue.Queue(maxsize=1)

        # Internal state flags
        self._is_inattent: bool = False   # Latest detection result
        self._lock = Lock()               # Lock for synchronizing thread-safe state updates

        # Worker thread
        self._running = True
        self._thread = Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def _worker_loop(self):
        """Background thread: waits for tasks in the queue and processes them."""
        while self._running:
            try:
                # Block until a task arrives (ignore task contents, it's just a signal)
                _ = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue  # check running flag again

            try:
                img_gray = self.cam.next_grayscale()
                results = self.detector.predict(img_gray)

                # Default: driver is not attentive
                is_inattent = True
                for detection in results:
                    if detection.label == 1:  
                        is_inattent = False

                with self._lock:
                    self._is_inattent = is_inattent

            finally:
                self._queue.task_done()

    def detect(self) -> bool:
        """
        Run an asynchronous detection if not already in progress.

        Returns
        -------
        bool
            The most recent detection result (True if inattentive, False if attentive).

        Notes
        -----
        - If called while detection is ongoing, it will simply return the last
          available result.
        """

        if self._queue.empty():
            try:
                self._queue.put_nowait(True)
            except queue.Full:
                pass  # shouldn't happen with maxsize=1

        with self._lock:
            return self._is_inattent

    def close(self):
        """Stop the worker thread gracefully."""
        self.cam.close()
        self._running = False
        self._thread.join(timeout=1.0)

class WebcamCameraStream(CameraStream):
    """
    Webcam camera stream using OpenCV.

    Parameters
    ----------
    device : int
        Camera device index (default 0).
    width, height : Optional[int]
        If provided, attempt to set capture resolution.
    flip : bool
        If True, flip the frame horizontally (useful for webcams).
    """

    def __init__(
        self,
        device: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        flip: bool = False,
    ):
        self.device = device
        self.flip = flip
        self.logger = logging.getLogger(__name__)
        self._default_frame = np.zeros((100, 100, 3), np.uint8)

        self._cap: Optional[cv2.VideoCapture] = cv2.VideoCapture(self.device)
        if not self._cap.isOpened():
            self._cap = None
            self.logger.warning("Could not open camera device %s", self.device)
            return

        # Optionally set resolution
        if width is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        if height is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))


    def next(self) -> np.ndarray:
        """
        Return next color frame (BGR) as a numpy ndarray.

        Returns black frame if frame could not be read.
        """
        if self._cap is None:
            self.logger.warning("Failed to read frame from camera.")
            return self._default_frame
        
        ret, frame = self._cap.read()

        if not ret or frame is None:
            self.logger.warning("Failed to read frame from camera.")
            return self._default_frame
        
        if self.flip:
            frame = cv2.flip(frame, 1)
        return frame

    def next_grayscale(self) -> np.ndarray:
        """
        Return the next frame converted to grayscale.
        """
        color = self.next()
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        return gray

    def close(self) -> None:
        """Release camera."""
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
