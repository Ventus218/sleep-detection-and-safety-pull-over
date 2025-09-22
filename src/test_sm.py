from enum import StrEnum, auto
from time import sleep
from typing import override
from sync_state_machine import Context, State, SyncStateMachine, Transition


class CarTimers(StrEnum):
    TURN_ON = auto()


class CarData:
    speed: float

    def __init__(self, speed: float):
        self.speed = speed


class CarState(State[CarData, CarTimers]): ...


class CarTransition(Transition[CarData, CarTimers]): ...


class ManualState(CarState):
    @override
    def parent(self) -> CarState | None:
        return CarTurnedOnState()

    @override
    def on_do(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        data.speed = data.speed + 10 * ctx.dt
        return data

    @override
    def transitions(self) -> list[CarTransition]:
        return [
            CarTransition(
                to=lambda: LaneKeepingState(),
                condition=lambda data, ctx: data.speed > 50,
            )
        ]


class LaneKeepingState(CarState):
    @override
    def parent(self) -> CarState | None:
        return CarTurnedOnState()

    @override
    def on_do(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        data.speed = data.speed + 1 * ctx.dt
        return data

    @override
    def transitions(self) -> list[CarTransition]:
        return [
            CarTransition(
                to=lambda: PullingOverState(),
                condition=lambda data, ctx: data.speed > 55,
                action=lambda data, ctx: (print("WARNING: pulling over"), data)[1],
            )
        ]


class PullingOverState(CarState):
    @override
    def parent(self) -> CarState | None:
        return CarTurnedOnState()

    @override
    def on_do(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        data.speed = data.speed - 10 * ctx.dt
        return data

    @override
    def transitions(self) -> list[CarTransition]:
        return [
            CarTransition(
                to=lambda: StoppedState(),
                condition=lambda data, ctx: data.speed <= 0,
            )
        ]


class StoppedState(CarState):
    @override
    def parent(self) -> CarState | None:
        return CarTurnedOnState()

    @override
    def on_entry(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        data.speed = 0
        return data


class CarTurnedOnState(CarState):
    @override
    def entry_child(self) -> CarState | None:
        return ManualState()

    @override
    def parent(self) -> CarState | None:
        return IAmACarState()

    @override
    def on_do(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print(f"speed: {data.speed}")
        return data

    @override
    def on_entry(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print("entering: TurnedOnState")
        return data

    @override
    def on_exit(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print("exiting: TurnedOnState")
        return data


class CarTurnedOffState(CarState):
    @override
    def parent(self) -> CarState | None:
        return IAmACarState()

    @override
    def on_entry(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print("entering: TurnedOffState")
        ctx.timer(CarTimers.TURN_ON).reset(5)
        print("turn on car in 5 seconds")
        return data

    @override
    def on_exit(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print("exiting: TurnedOffState")
        return data

    @override
    def transitions(self) -> list[CarTransition]:
        return [
            CarTransition(
                to=lambda: CarTurnedOnState(),
                condition=lambda data, ctx: ctx.timer(CarTimers.TURN_ON).is_elapsed(),
            )
        ]


class IAmACarState(CarState):
    @override
    def entry_child(self) -> CarState | None:
        return CarTurnedOffState()

    @override
    def on_entry(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print("entering: IAmACarState")
        return data

    @override
    def on_exit(self, data: CarData, ctx: Context[CarTimers]) -> CarData:
        print("exiting: IAmACarState")
        return data


class VehicleSM(SyncStateMachine[CarData, CarTimers]):
    def __init__(self, data: CarData):
        super().__init__(IAmACarState(), data)


if __name__ == "__main__":
    vehicle = VehicleSM(CarData(speed=30))
    while True:
        sleep(0.1)
        print(vehicle.step(0.1).speed)
