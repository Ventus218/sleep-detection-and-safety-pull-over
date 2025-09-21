from __future__ import annotations
from abc import ABC
from typing import Protocol, final


class Condition[Data](Protocol):
    def __call__(self, data: Data) -> bool: ...


class MakeNextState[Data](Protocol):
    def __call__(self) -> State[Data]: ...


class Action[Data](Protocol):
    def __call__(self, data: Data) -> Data: ...


class Transition[Data]:
    condition: Condition[Data]

    make_next_state: MakeNextState[Data]

    action: Action[Data]

    def __init__(
        self,
        to: MakeNextState[Data],
        condition: Condition[Data] = lambda data: True,
        action: Action[Data] = lambda data: data,
    ) -> None:
        self.make_next_state = to
        self.condition = condition
        self.action = action


class State[Data](ABC):
    def on_entry(self, dt: float, data: Data) -> Data:  # pyright: ignore[reportUnusedParameter]
        return data

    def on_do(self, dt: float, data: Data) -> Data:  # pyright: ignore[reportUnusedParameter]
        return data

    def on_exit(self, dt: float, data: Data) -> Data:  # pyright: ignore[reportUnusedParameter]
        return data

    def transitions(self) -> list[Transition[Data]]:
        return list()


class SyncStateMachine[Data](ABC):
    __state: State[Data]
    __data: Data

    def __init__(self, state: State[Data], data: Data):
        self.__state = state
        self.__data = self.__state.on_entry(dt=0, data=data)

    @final
    def step(self, dt: float) -> Data:
        transition = next(
            (t for t in self.__state.transitions() if t.condition(self.__data)), None
        )
        if transition is not None:
            self.__data = self.__state.on_exit(dt, self.__data)
            self.__data = transition.action(self.__data)
            self.__state = transition.make_next_state()
            self.__data = self.__state.on_entry(dt, self.__data)
        self.__data = self.__state.on_do(dt, self.__data)
        return self.__data
