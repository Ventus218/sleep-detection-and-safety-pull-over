import math
import numpy as np
import threading
from .utils import RansacPlaneFit

# Assume RansacPlaneFit, fit_plane_ransac, point_plane_distance
# are available in your environment


class SafePulloverChecker:
    """
    Decide if pulling over is safe using a single radar sensor and RANSAC plane fitting.

    Workflow:
      - Collect radar points from the sensor.
      - Use RANSAC to fit a plane (guardrail or road boundary).
      - Decide safety based on inlier/outlier statistics:
          * Require a minimum number of inliers.
          * Require an inlier ratio above a threshold.
    """

    def __init__(
        self,
        radar_sensor,
        inlier_dist_thresh: float = 0.3,
        min_inlier_ratio: float = 0.6,
        min_inliers: int = 20,
        ransac_max_trials: int = 400,
        debug: bool = False,
    ):
        self.radar_sensor = radar_sensor
        self.inlier_dist_thresh = float(inlier_dist_thresh)
        self.min_inlier_ratio = float(min_inlier_ratio)
        self.min_inliers = int(min_inliers)
        self.ransac_max_trials = int(ransac_max_trials)
        self.debug = bool(debug)

        # buffer for latest radar points
        self._lock = threading.Lock()
        self._latest_points: np.ndarray = np.zeros((0, 3), dtype=np.float32)

        if self.radar_sensor:
            self.radar_sensor.listen(self._callback)

    def _debug(self, msg):
        if self.debug:
            print(msg)

    # ------------------------------
    # Radar callback
    # ------------------------------
    def _callback(self, radar_measurement):
        """Convert CARLA radar detections to Nx3 numpy array and store them."""
        pts = []
        for detection in radar_measurement:
            # conversion from polar to cartesian coordinates
            d = float(detection.depth)
            az = float(detection.azimuth)
            alt = float(detection.altitude)
            ca = math.cos(alt)
            x = d * ca * math.cos(az)
            y = d * ca * math.sin(az)
            z = d * math.sin(alt)
            pts.append((x, y, z))
        arr = np.asarray(pts, dtype=np.float32)
        with self._lock:
            self._latest_points = arr

    # ------------------------------
    # Main decision
    # ------------------------------
    def is_pullover_safe(self) -> bool:
        """Return True if pullover is considered safe, False otherwise."""
        with self._lock:
            pts = self._latest_points.copy()

        if pts.shape[0] < self.min_inliers:
            self._debug("Not enough radar points.")
            return False

        # fit plane using RANSAC
        ransac = RansacPlaneFit(pts, self.inlier_dist_thresh, self.ransac_max_trials)

        if not ransac.has_found_plane:
            self._debug("Plane fitting failed.")
            return False

        inlier_ratio = ransac.num_inliers / float(ransac.num_points)
        self._debug(f"Inliers: {ransac.num_inliers}/{ransac.num_points} "
                  f"({inlier_ratio:.2f}), Distance={ransac.distance:.2f}")

        # check thresholds
        if ransac.num_inliers < self.min_inliers:
            self._debug("Not enough inliers.")
            return False

        if inlier_ratio < self.min_inlier_ratio:
            self._debug("Inlier ratio too low.")
            return False

        self._debug("Safe to pull over.")
        return True


    def destroy(self):
        try:
            if self.radar_sensor:
                self.radar_sensor.stop()
        except Exception:
            pass

    def __del__(self):
        self.destroy()
