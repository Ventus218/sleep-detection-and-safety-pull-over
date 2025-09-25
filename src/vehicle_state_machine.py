from enum import StrEnum, auto
from typing import override

from carla import Vector3D, Vehicle, VehicleControl

from sync_state_machine import Context, State, StateAction, Transition


class VehicleData:
    speed: Vector3D = Vector3D()
    should_toggle_lane_keeping: bool = False
    should_enter_manual_driving: bool = False

    vehicle_actor: Vehicle
    vehicle_control: VehicleControl

    def __init__(self, vehicle_actor: Vehicle, vehicle_control: VehicleControl):
        self.vehicle_actor = vehicle_actor
        self.vehicle_control = vehicle_control


class VehicleTimers(StrEnum):
    INATTENTION = auto()


type VehicleContext = Context[VehicleTimers]


class VehicleState(State[VehicleData, VehicleTimers]): ...


class VehicleStateAction(StateAction[VehicleData, VehicleTimers]): ...


class VehicleTransition(Transition[VehicleData, VehicleTimers]): ...


class WrapperS(State[VehicleData, VehicleTimers]):
    @override
    def children(self) -> list[VehicleState]:
        return [ManualDrivingS(), LaneKeepingS(), PullingOverS(), StoppedS()]

    @override
    def on_early_do(self, data: VehicleData, ctx: VehicleContext):
        data.speed = data.vehicle_actor.get_velocity()
        data.vehicle_control = VehicleControl()

    @override
    def on_late_do(self, data: VehicleData, ctx: VehicleContext):
        data.vehicle_actor.apply_control(data.vehicle_control)


# ========== MANUAL_DRIVING ==========


class ManualDrivingS(VehicleState):
    @override
    def children(self) -> list[VehicleState]:
        return [LaneKeepingS()]

    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=LaneKeepingS(),
                condition=lambda data, ctx: data.should_toggle_lane_keeping,
            )
        ]


# ========== LANE_KEEPING ==========


class LaneKeepingS(VehicleState):
    @override
    def children(self) -> list[VehicleState]:
        return [
            NoInattentionDetectedS(),
            InattentionDetectedS(),
            PullOverPreparationS(),
        ]

    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=ManualDrivingS(),
                condition=lambda data, ctx: data.should_toggle_lane_keeping,
            )
        ]


def _inattention_detected(data: VehicleData) -> bool:
    # TODO
    return True


class NoInattentionDetectedS(VehicleState):
    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=InattentionDetectedS(),
                condition=lambda data, ctx: _inattention_detected(data),
            )
        ]


class InattentionDetectedS(VehicleState):
    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=NoInattentionDetectedS(),
                condition=lambda data, ctx: not _inattention_detected(data),
            ),
            VehicleTransition(
                to=PullOverPreparationS(),
                condition=lambda data, ctx: ctx.timer(
                    VehicleTimers.INATTENTION
                ).is_elapsed(),
            ),
        ]

    @override
    def on_entry(self, data: VehicleData, ctx: VehicleContext):
        # TODO: choose proper amount of seconds
        ctx.timer(VehicleTimers.INATTENTION).reset(5)


def _pull_over_is_safe(data: VehicleData) -> bool:
    # TODO
    return True


class PullOverPreparationS(VehicleState):
    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=PullingOverS(),
                condition=lambda data, ctx: _pull_over_is_safe(data),
            )
        ]


# ========== PULLING_OVER ==========


class PullingOverS(VehicleState):
    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=ManualDrivingS(),
                condition=lambda data, ctx: data.should_enter_manual_driving,
            )
        ]


# ========== STOPPED ==========


class StoppedS(VehicleState):
    @override
    def transitions(self) -> list[VehicleTransition]:
        return [
            VehicleTransition(
                to=ManualDrivingS(),
                condition=lambda data, ctx: data.should_enter_manual_driving,
            )
        ]
