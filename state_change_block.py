from .state_change_base_block import StateChangeBase
from nio.common.discovery import Discoverable, DiscoverableType
from nio.modules.threading import Lock
from nio.metadata.properties.bool import BoolProperty


# NB: This is not discoverable. Is it needed?
class StateChangeVolatile(StateChangeBase):
    def process_signals(self, signals):
        for signal in signals:
            try:
                out = self._process_state(signal)
            except Exception as e:
                self.log_error(e)
                continue
            if out is not None:
                self.notify_signals([out])
                

@Discoverable(DiscoverableType.block)
class StateChange(StateChangeBase):
    """ Notifies a signal on *state* change.

    Maintains a *state*. When *state* changes, a signal is notified
    that containes the *state* and *prev_state*.

    *state* is set by the *state_expr* property. It is an expression
    property that evalues to *state*. If the expression fails,
    then the *state* remains unmodified.

    *state* changing from None to not None does not count as a state change.
    This makes is so that setting the initial state does not trigger
    a notification Signal.
    """

    exclude = BoolProperty(default=True, title = "Exclude Existing Fields")
    use_persistence = BoolProperty(title="Use Persistence", default=True,
            visible=True)

    def __init__(self):
        super().__init__()
        self._safe_lock = Lock()

    def process_signals(self, signals):
        self._logger.debug(
            "Ready to process {} incoming signals".format(len(signals))
        )
        with self._safe_lock:
            for signal in signals:
                self._logger.debug("Attempting to set state")
                out = self._process_state(signal, self.exclude)
                if out is not None:
                    self.notify_signals([out])
