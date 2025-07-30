import enum


class WebSocketActions(str, enum.Enum):
    """Действия, которые может инициировать клиент."""
    JOIN = "join"
    SUBMIT_VARIANT = "submit_variant"


class WebSocketEvents(str, enum.Enum):
    """События, которые сервер отправляет клиентам."""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    VARIANT_SUBMITTED = "variant_submitted"
    TIMER_STARTED = "timer_started"
    TIMER_FINISHED = "timer_finished"
    VARIANT_ELIMINATED = "variant_eliminated"
    WINNER_DECLARED = "winner_declared"
    ROULETTE_CANCELLED = "roulette_cancelled"
    ERROR = "error"


VARIANT_SUBMISSION_TIMOUT_SECONDS = 60
ROULETTE_ELIMINATION_PAUSE_SECONDS = 3


