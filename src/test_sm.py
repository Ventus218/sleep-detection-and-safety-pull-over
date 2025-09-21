from time import sleep
from typing import override
from sync_state_machine import State, SyncStateMachine, Transition


class CarData:
    speed: float

    def __init__(self, speed: float):
        self.speed = speed


class ManualState(State[CarData]):
    @override
    def on_do(self, dt: float, data: CarData) -> CarData:
        data.speed = data.speed + 10 * dt
        return data

    @override
    def transitions(self) -> list[Transition[CarData]]:
        return [
            Transition[CarData](
                to=lambda: LaneKeepingState(),
                condition=lambda data: data.speed > 50,
                action=lambda data: (print("Transitioning to LaneKeeping"), data)[1],
            )
        ]


class LaneKeepingState(State[CarData]):
    @override
    def on_do(self, dt: float, data: CarData) -> CarData:
        data.speed = data.speed + 1 * dt
        return data

    @override
    def transitions(self) -> list[Transition[CarData]]:
        return [
            Transition[CarData](
                to=lambda: PullingOverState(),
                condition=lambda data: data.speed > 55,
                action=lambda data: (print("Transitioning to PullingOver"), data)[1],
            )
        ]


class PullingOverState(State[CarData]):
    @override
    def on_do(self, dt: float, data: CarData) -> CarData:
        data.speed = data.speed - 10 * dt
        return data

    @override
    def transitions(self) -> list[Transition[CarData]]:
        return [
            Transition[CarData](
                to=lambda: StoppedState(),
                condition=lambda data: data.speed <= 0,
                action=lambda data: (print("Transitioning to Stopped"), data)[1],
            )
        ]


class StoppedState(State[CarData]):
    pass


class VehicleSM(SyncStateMachine[CarData]):
    def __init__(self, data: CarData):
        super().__init__(ManualState(), data)


if __name__ == "__main__":
    vehicle = VehicleSM(CarData(speed=30))
    while True:
        sleep(0.1)
        print(vehicle.step(0.1).speed)
