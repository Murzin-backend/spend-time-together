import enum

class ActivityStatuses(enum.StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class ActivityTypes(enum.StrEnum):
    BOARD_GAMES = "board_games"
    VIDEO_GAMES = "video_games"
    MOVIES = "movies"

    @property
    def is_active_type(self) -> bool:
        return self in {ActivityTypes.VIDEO_GAMES}
