class LoggingConfig:
    _log_entries: bool
    _log_early_dos: bool
    _log_dos: bool
    _log_late_dos: bool
    _log_exits: bool
    _log_transitions: bool
    _log_transition_actions: bool
    _log_state_actions: bool

    @property
    def log_entries(self) -> bool:
        return self._log_entries

    @property
    def log_early_dos(self) -> bool:
        return self._log_early_dos

    @property
    def log_dos(self) -> bool:
        return self._log_dos

    @property
    def log_late_dos(self) -> bool:
        return self._log_late_dos

    @property
    def log_exits(self) -> bool:
        return self._log_exits

    @property
    def log_transitions(self) -> bool:
        return self._log_transitions

    @property
    def log_transition_actions(self) -> bool:
        return self._log_transition_actions

    @property
    def log_state_actions(self) -> bool:
        return self._log_state_actions

    def __init__(
        self,
        log_entries: bool = False,
        log_early_dos: bool = False,
        log_dos: bool = False,
        log_late_dos: bool = False,
        log_exits: bool = False,
        log_transitions: bool = False,
        log_transition_actions: bool = False,
        log_state_actions: bool = False,
    ):
        self._log_entries = log_entries
        self._log_early_dos = log_early_dos
        self._log_dos = log_dos
        self._log_late_dos = log_late_dos
        self._log_exits = log_exits
        self._log_transitions = log_transitions
        self._log_transition_actions = log_transition_actions
        self._log_state_actions = log_state_actions
