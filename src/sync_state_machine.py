from __future__ import annotations
from abc import ABC
from collections.abc import Sequence
from typing import Protocol, cast, final, override


class Condition[Data, Timers](Protocol):
    def __call__(self, data: Data, ctx: Context[Timers]) -> bool: ...


class MakeNextState[Data, Timers](Protocol):
    def __call__(self) -> State[Data, Timers]: ...


class Action[Data, Timers](Protocol):
    def __call__(self, data: Data, ctx: Context[Timers]) -> Data: ...


class Transition[Data, Timers]:
    condition: Condition[Data, Timers]

    make_next_state: MakeNextState[Data, Timers]

    action: Action[Data, Timers]

    def __init__(
        self,
        to: MakeNextState[Data, Timers],
        condition: Condition[Data, Timers] = lambda data, ctx: True,
        action: Action[Data, Timers] = lambda data, ctx: data,
    ) -> None:
        self.make_next_state = to
        self.condition = condition
        self.action = action


class State[Data, Timers](ABC):
    def parent(self) -> State[Data, Timers] | None:
        return None

    def entry_child(self) -> State[Data, Timers] | None:
        return None

    def on_entry(self, data: Data, ctx: Context[Timers]) -> Data:  # pyright: ignore[reportUnusedParameter]
        return data

    def on_do(self, data: Data, ctx: Context[Timers]) -> Data:  # pyright: ignore[reportUnusedParameter]
        return data

    def on_exit(self, data: Data, ctx: Context[Timers]) -> Data:  # pyright: ignore[reportUnusedParameter]
        return data

    def transitions(self) -> Sequence[Transition[Data, Timers]]:
        return list()

    @final
    def ancestors(self) -> list[State[Data, Timers]]:
        return _ancestors_rec(self, [])

    # Equality just checks the type
    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, State):
            return NotImplemented
        return type(self) is type(cast(State[Data, Timers], value))

    @override
    def __hash__(self) -> int:
        return hash(type(self))


def _ancestors_rec[D, T](
    child: State[D, T], acc: list[State[D, T]]
) -> list[State[D, T]]:
    match child.parent():
        case None:
            return acc
        case parent:
            return _ancestors_rec(parent, acc + [parent])


def _lowest_common_ancestor[D, T](
    s1: State[D, T], s2: State[D, T]
) -> State[D, T] | None:
    ancestors_2 = set(s2.ancestors())
    for p1 in s1.ancestors():
        if ancestors_2.__contains__(p1):
            return p1


def _lowest_entry_child[D, T](s: State[D, T]) -> State[D, T]:
    entry_child = s.entry_child()
    if entry_child is None:
        return s
    else:
        return _lowest_entry_child(entry_child)


class Context[Timers]:
    _dt: float
    _timers: dict[Timers, Timer] = {}

    @property
    def dt(self):
        return self._dt

    def timer(self, timer: Timers) -> Timer:
        t = self._timers.get(timer)
        match t:
            case None:
                self._timers[timer] = Timer(0)
                return self._timers[timer]
            case t:
                return t

    def _step(self, dt: float):
        self._dt = dt
        for t in self._timers.values():
            t.step(self._dt)

    def __init__(self, dt: float):
        self._dt = dt


class SyncStateMachine[Data, Timers](ABC):
    __state: State[Data, Timers]
    __data: Data
    __context: Context[Timers]

    def __init__(self, state: State[Data, Timers], data: Data):
        self.__state = _lowest_entry_child(state)
        self.__data = data
        self.__context = Context(0)
        self.__data = self.__entry_states(
            list(reversed(self.__state.ancestors())) + [self.__state], self.__context
        )

    def __entry_states(
        self, states: list[State[Data, Timers]], ctx: Context[Timers]
    ) -> Data:
        for s in states:
            self.__data = s.on_entry(self.__data, ctx)
        return self.__data

    @final
    def step(self, dt: float) -> Data:
        self.__context._step(dt)  # pyright: ignore[reportPrivateUsage]
        transition = next(
            (
                t
                for t in self.__state.transitions()
                if t.condition(self.__data, self.__context)
            ),
            None,
        )
        if transition is not None:
            next_state = transition.make_next_state()
            next_state = _lowest_entry_child(next_state)
            lca = _lowest_common_ancestor(self.__state, next_state)

            # exit from state and from all ancestors up to the lowest common ancestor
            self.__data = self.__state.on_exit(self.__data, self.__context)
            for p in self.__state.ancestors():
                if lca is None or lca == p:
                    break
                else:
                    self.__data = lca.on_exit(self.__data, self.__context)

            self.__data = transition.action(self.__data, self.__context)
            self.__state = next_state

            # entry into all ancestors down from the lowest common ancestor and then into state
            reversed_ancestors = list(reversed(self.__state.ancestors()))
            if lca is not None:
                # removing lca and outer ancestor
                while reversed_ancestors.pop(0) != lca:
                    ...
            self.__data = self.__entry_states(
                reversed_ancestors + [self.__state], self.__context
            )

        # on_do for all ancestors down from the lowest common ancestor and then into state
        for p in list(reversed(self.__state.ancestors())):
            self.__data = p.on_do(self.__data, self.__context)
        self.__data = self.__state.on_do(self.__data, self.__context)
        return self.__data


class Timer:
    _time_set: float
    _time_left: float

    def __init__(self, time_set: float = 0):
        self._time_set = time_set
        self.reset(time_set)

    def reset(self, time_set: float | None = None):
        match time_set:
            case None:
                self._time_left = self._time_set
            case time_set:
                self._time_left = time_set

    def step(self, dt: float):
        if not self.is_elapsed():
            self._time_left = self._time_left - dt

    def is_elapsed(self) -> bool:
        return self._time_left <= 0
