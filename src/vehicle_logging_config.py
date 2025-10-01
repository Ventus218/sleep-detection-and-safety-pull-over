from state_machine.logging_config import LoggingConfig


class VehicleLoggingConfig(LoggingConfig):
    _log_main_vehicle_controls: bool

    @property
    def log_main_vehicle_controls(self):
        return self._log_main_vehicle_controls

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
        log_main_vehicle_controls: bool = False,
    ):
        super().__init__(
            log_entries=log_entries,
            log_early_dos=log_early_dos,
            log_dos=log_dos,
            log_late_dos=log_late_dos,
            log_exits=log_exits,
            log_transitions=log_transitions,
            log_transition_actions=log_transition_actions,
            log_state_actions=log_state_actions,
        )
        self._log_main_vehicle_controls = log_main_vehicle_controls
