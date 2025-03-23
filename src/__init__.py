# __init__.py

# Import the core functionalities of the EcmaTimer package
from .EcmaTimer import (
    SetTimer,
    SetTimerEx,
    KillTimer,
    HandleTimerError,
    IsValidTimer,
    IsRepeatingTimer,
    CountRunningTimers,
    CountSetTimerRunning,
    CountSetTimerExRunning,
    SetDependentTimer,
    SetTimerWithPriority,
    SetCancelableTimer,
    PauseTimer,
    ResumeTimer,
    SetTimerWithErrorHandling
)

# Import error classes for custom exceptions
from .EcmaTimer import (
    TimerError,
    InvalidFunctionError,
    TimerNotFoundError,
    InvalidIntervalError
)

# You can also include additional package-wide variables or constants here
__version__ = "1.0.0"
