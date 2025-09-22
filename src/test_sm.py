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
    def on_do(self, data: CarData, ctx: Context[CarTimers]):
        data.speed = data.speed + 10 * ctx.dt

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
    def on_do(self, data: CarData, ctx: Context[CarTimers]):
        data.speed = data.speed + 1 * ctx.dt

    @override
    def transitions(self) -> list[CarTransition]:
        return [
            CarTransition(
                to=lambda: PullingOverState(),
                condition=lambda data, ctx: data.speed > 55,
                action=lambda data, ctx: print("WARNING: pulling over"),
            )
        ]


class PullingOverState(CarState):
    @override
    def parent(self) -> CarState | None:
        return CarTurnedOnState()

    @override
    def on_do(self, data: CarData, ctx: Context[CarTimers]):
        data.speed = data.speed - 10 * ctx.dt

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
    def on_entry(self, data: CarData, ctx: Context[CarTimers]):
        data.speed = 0


class CarTurnedOnState(CarState):
    @override
    def entry_child(self) -> CarState | None:
        return ManualState()

    @override
    def parent(self) -> CarState | None:
        return IAmACarState()

    @override
    def on_do(self, data: CarData, ctx: Context[CarTimers]):
        print(f"speed: {data.speed}")

    @override
    def on_entry(self, data: CarData, ctx: Context[CarTimers]):
        print("entering: TurnedOnState")

    @override
    def on_exit(self, data: CarData, ctx: Context[CarTimers]):
        print("exiting: TurnedOnState")


class CarTurnedOffState(CarState):
    @override
    def parent(self) -> CarState | None:
        return IAmACarState()

    @override
    def on_entry(self, data: CarData, ctx: Context[CarTimers]):
        print("entering: TurnedOffState")
        ctx.timer(CarTimers.TURN_ON).reset(5)
        print("turn on car in 5 seconds")

    @override
    def on_exit(self, data: CarData, ctx: Context[CarTimers]):
        print("exiting: TurnedOffState")

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
    def on_entry(self, data: CarData, ctx: Context[CarTimers]):
        print("entering: IAmACarState")

    @override
    def on_exit(self, data: CarData, ctx: Context[CarTimers]):
        print("exiting: IAmACarState")


class VehicleSM(SyncStateMachine[CarData, CarTimers]):
    def __init__(self, data: CarData):
        super().__init__(IAmACarState(), data)


if __name__ == "__main__":
    vehicle = VehicleSM(CarData(speed=30))
    while True:
        sleep(0.1)
        print(vehicle.step(0.1).speed)
