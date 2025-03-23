"""
******************************************************************************
* EcmaTimer
* 
* Copyright (c) 2025 Abolfazl Hosseini. All rights reserved.
*
* This software is licensed under the MIT License. You are free to use, modify,
* and distribute this software, but please provide attribution and include a 
* copy of this license in any copies of the software that you distribute.
* 
* The Timer Management System provides a collection of utilities for creating, 
* managing, and controlling timers with various features such as priorities, 
* dependencies, cancellation, and more. It is designed to be easy to integrate 
* into Python-based asynchronous applications.
* 
* You may not use this software for unlawful purposes or in a way that may 
* violate any laws or third-party rights.
*
* DISCLAIMER: This software is provided "as-is" without warranty of any kind, 
* either expressed or implied, including but not limited to the warranties 
* of merchantability, fitness for a particular purpose, or noninfringement. 
* In no event shall the authors or copyright holders be liable for any claim, 
* damages, or other liability, whether in an action of contract, tort, or otherwise, 
* arising from, out of, or in connection with the software or the use or other dealings 
* in the software.
*
* Version: 1.0.0
* Author: Abolfazl Hosseini
* Date: 2025 23 March
******************************************************************************
"""


import time
import asyncio
from queue import PriorityQueue

class TimerError(Exception):
    """
    Custom exception for timer-related errors.
    """
    def __init__(self, message, timer_id=None):
        self.message = message
        self.timer_id = timer_id
        super().__init__(self.message)

class InvalidFunctionError(TimerError):
    """
    Exception raised when a provided function is not callable.
    """
    def __init__(self, message="Function must be callable"):
        self.message = message
        super().__init__(self.message)

class TimerNotFoundError(TimerError):
    """
    Exception raised when a timer ID is not found.
    """
    def __init__(self, timer_id):
        self.message = f"Timer with ID {timer_id} not found."
        self.timer_id = timer_id
        super().__init__(self.message)

class InvalidIntervalError(TimerError):
    """
    Exception raised when the interval is not a positive number.
    """
    def __init__(self, interval):
        self.message = f"Interval must be a positive number. Given: {interval}"
        super().__init__(self.message)


# Global Variables

timers = {}
"""
Dictionary to store all active timers.
Key: Timer ID
Value: Dictionary containing timer details (repeating, function name, arguments, etc.)
"""

timer_counter = 1
"""
Global counter to generate unique timer IDs.
Incremented every time a new timer is set.
"""

set_timer_count = 0
"""
Keeps track of the number of standard timers set.
This is incremented each time a standard timer is set.
"""

set_timer_ex_count = 0
"""
Keeps track of the number of extended timers (SetTimerEx) set.
This is incremented each time an extended timer is set.
"""

lock = asyncio.Lock()
"""
An asyncio lock to ensure thread-safe operations when modifying shared variables, especially for timers.
"""

global_settings = {'min_interval': 100, 'max_repeats': 5}
"""
Global settings dictionary containing the minimum interval for timers (in milliseconds) and the maximum number of repeats for timers.
- 'min_interval': Minimum allowed interval between timer executions.
- 'max_repeats': Maximum number of times a repeating timer can run.
"""

priority_queue = PriorityQueue()
"""
Priority Queue to manage timers with different priorities.
Timers with higher priority values are executed first.
Used in functions like SetTimerWithPriority.
"""

paused_timers = {}
"""
Dictionary to store paused timers.
Key: Timer ID
Value: Dictionary containing timer details and remaining time when paused.
"""

timer_dependencies = {}
"""
Dictionary to store dependencies between timers.
Key: Timer ID
Value: List of dependent timer IDs that should start after the key timer completes.
"""

async def timer_function(function_name, interval, repeating=False):
    """
    Executes the provided function after the specified interval.
    If 'repeating' is True, schedules itself again.

    :param function_name: The function to execute.
    :param interval: Interval in seconds.
    :param repeating: Whether the timer should repeat.
    """
    try:
        await function_name()
        if repeating:
            await SetTimer(function_name, interval, repeating=True)
    except Exception as e:
        raise TimerError(f"Error in timer function: {e}")

async def SetTimer(function_name, interval, repeating=False, depends_on=None):
    """
    Sets a timer to call a function after a specified time. Can be set to repeat.

    :param function_name: Function to call. This must be callable.
    :param interval: Interval in milliseconds.
    :param repeating: Whether the timer should repeat.
    :param depends_on: Timer ID this timer depends on.
    :return: Timer ID.
    
    Example:
    >>> async def my_function():
    >>>     print("Hello")
    >>> timer_id = await SetTimer(my_function, 2000, repeating=True)
    """
    global timer_counter, set_timer_count
    if not function_name or not callable(function_name):
        raise InvalidFunctionError()

    if interval <= 0:
        raise InvalidIntervalError(interval)
    
    timer_id = timer_counter
    timer_counter += 1

    # Register the dependencies for this timer
    if depends_on:
        if depends_on not in timers:
            raise TimerNotFoundError(depends_on)
        if depends_on not in timer_dependencies:
            timer_dependencies[depends_on] = []
        timer_dependencies[depends_on].append(timer_id)

    # Create an asynchronous task for the timer
    asyncio.create_task(timer_function(function_name, interval / 1000, repeating))
    
    timers[timer_id] = {'repeating': repeating, 'function_name': function_name, 'depends_on': depends_on}
    set_timer_count += 1
    
    return timer_id

async def SetTimerEx(function_name, interval, repeating=False, *args, specifiers=None, depends_on=None):
    """
    Sets an advanced timer to call a function with arguments after a specified interval.
    Supports function dependencies and optional arguments.
    
    :param function_name: Callable function to execute.
    :param interval: Interval in milliseconds.
    :param repeating: Boolean indicating if the function should repeat.
    :param args: Additional arguments to pass to the function.
    :param specifiers: Optional parameter for special handling (not implemented yet).
    :param depends_on: Timer ID that this timer depends on.
    :return: Timer ID.
    """
    global timer_counter, set_timer_ex_count
    if not function_name or not callable(function_name):
        raise InvalidFunctionError()

    if interval <= 0:
        raise InvalidIntervalError(interval)
    
    async def timer_function_ex():
        try:
            await function_name(*args)
            if repeating:
                await SetTimerEx(function_name, interval, repeating=True, specifiers=specifiers, depends_on=depends_on, *args)
        except Exception as e:
            raise TimerError(f"Error in timer function: {e}")
    
    timer_id = timer_counter
    timer_counter += 1

    if depends_on:
        if depends_on not in timers:
            raise TimerNotFoundError(depends_on)
        if depends_on not in timer_dependencies:
            timer_dependencies[depends_on] = []
        timer_dependencies[depends_on].append(timer_id)

    asyncio.create_task(timer_function_ex())
    
    timers[timer_id] = {'repeating': repeating, 'function_name': function_name, 'args': args, 'depends_on': depends_on}
    set_timer_ex_count += 1
    
    return timer_id

async def KillTimer(timer_id):
    """
    Stops a running timer by its ID.

    :param timer_id: Timer ID to be stopped.
    :return: 0 if successful.
    
    Example:
    >>> await KillTimer(timer_id)
    """
    global set_timer_count, set_timer_ex_count
    if timer_id not in timers:
        raise TimerNotFoundError(timer_id)
    
    try:
        del timers[timer_id]
        if timers[timer_id]['function_name'] == SetTimer:
            set_timer_count -= 1
        elif timers[timer_id]['function_name'] == SetTimerEx:
            set_timer_ex_count -= 1

        if timer_id in timer_dependencies:
            for dependent_timer_id in timer_dependencies[timer_id]:
                await KillTimer(dependent_timer_id)
            del timer_dependencies[timer_id]
    except Exception as e:
        raise TimerError(f"Failed to kill timer {timer_id}: {e}")
    
    return 0

async def HandleTimerError(timer_id, error_message):
    """
    Handles errors in timers and terminates dependent timers.
    
    :param timer_id: The ID of the timer that encountered an error.
    :param error_message: The error message describing the issue.
    """
    print(f"Error in timer {timer_id}: {error_message}")
    if timer_id in timer_dependencies:
        for dependent_timer_id in timer_dependencies[timer_id]:
            await KillTimer(dependent_timer_id)

def IsValidTimer(timer_id):
    """
    Checks if a given timer ID is valid.
    
    :param timer_id: The ID of the timer to check.
    :return: True if the timer exists, raises TimerNotFoundError otherwise.
    """
    if timer_id not in timers:
        raise TimerNotFoundError(timer_id)
    return True

def IsRepeatingTimer(timer_id):
    """
    Checks if a given timer is a repeating timer.
    
    :param timer_id: The ID of the timer to check.
    :return: True if the timer is repeating, False otherwise.
    """
    if timer_id not in timers:
        raise TimerNotFoundError(timer_id)
    return timers[timer_id]['repeating']

def CountRunningTimers():
    """
    Returns the number of currently running timers.
    
    :return: The count of active timers.
    """
    return len(timers)

def CountSetTimerRunning():
    """
    Returns the number of timers set using SetTimer.
    
    :return: The count of SetTimer timers.
    """
    return set_timer_count

def CountSetTimerExRunning():
    """
    Returns the number of timers set using SetTimerEx.
    
    :return: The count of SetTimerEx timers.
    """
    return set_timer_ex_count

async def SetDependentTimer(function_name, interval, dependent_timer_id=None, repeating=False):
    """
    Sets a timer that starts only after another specified timer completes.
    
    :param function_name: Callable function to execute.
    :param interval: Interval in milliseconds.
    :param dependent_timer_id: The ID of the timer that must complete first.
    :param repeating: Boolean indicating if the function should repeat.
    """
    if dependent_timer_id:
        if dependent_timer_id not in timers:
            raise TimerNotFoundError(dependent_timer_id)
        
        def start_after_dependent():
            SetTimer(function_name, interval, repeating)
        
        timers[dependent_timer_id]['function'] = start_after_dependent
    else:
        return await SetTimer(function_name, interval, repeating)

async def SetTimerWithPriority(function_name, interval, repeating=False, priority=0, depends_on=None):
    """
    Sets a timer with priority, ensuring higher priority timers run first.
    
    :param function_name: Callable function to execute.
    :param interval: Interval in milliseconds.
    :param repeating: Boolean indicating if the function should repeat.
    :param priority: Integer priority value (higher numbers run first).
    :param depends_on: Timer ID that this timer depends on.
    """
    global timer_counter
    if not function_name or not callable(function_name):
        raise InvalidFunctionError()

    if interval <= 0:
        raise InvalidIntervalError(interval)
    
    async def timer_function_with_priority():
        try:
            await function_name()
            if repeating:
                await SetTimerWithPriority(function_name, interval, repeating=True, priority=priority, depends_on=depends_on)
        except Exception as e:
            raise TimerError(f"Error in timer function: {e}")
    
    timer_id = timer_counter
    timer_counter += 1

    # Register the dependencies for this timer
    if depends_on:
        if depends_on not in timers:
            raise TimerNotFoundError(depends_on)
        if depends_on not in timer_dependencies:
            timer_dependencies[depends_on] = []
        timer_dependencies[depends_on].append(timer_id)

    # Create an asynchronous task for the timer
    asyncio.create_task(timer_function_with_priority())
    
    with lock:
        timers[timer_id] = {'repeating': repeating, 'function_name': function_name, 'priority': priority, 'depends_on': depends_on}
    
    priority_queue.put((priority, timer_id, timers[timer_id]))
    
    while not priority_queue.empty():
        _, timer_id, timer_data = priority_queue.get()
        timer_data['timer'].start()
    
    return timer_id

async def SetCancelableTimer(function_name, interval, repeating=False, depends_on=None):
    """
    Sets a timer that can be canceled at any time.
    
    :param function_name: Callable function to execute.
    :param interval: Interval in milliseconds.
    :param repeating: Boolean indicating if the function should repeat.
    :param depends_on: Timer ID that this timer depends on.
    :return: Timer ID.
    """
    timer_id = await SetTimer(function_name, interval, repeating, depends_on)
    timers[timer_id]['cancelable'] = True
    return timer_id

async def PauseTimer(timer_id):
    """
    Pauses a running timer and stores the remaining time.
    
    :param timer_id: The ID of the timer to pause.
    """
    if timer_id not in timers:
        raise TimerNotFoundError(timer_id)

    remaining_time = timers[timer_id]['interval'] - time.time()
    await KillTimer(timer_id)
    timers[timer_id]['remaining_time'] = remaining_time

async def ResumeTimer(timer_id):
    """
    Resumes a previously paused timer with its remaining time.
    
    :param timer_id: The ID of the timer to resume.
    """
    if timer_id not in timers:
        raise TimerNotFoundError(timer_id)

    if 'remaining_time' in timers[timer_id]:
        await SetTimer(timers[timer_id]['function_name'], timers[timer_id]['remaining_time'], repeating=timers[timer_id]['repeating'])

async def SetTimerWithErrorHandling(function_name, interval, repeating=False, depends_on=None):
    """
    Sets a timer with error handling to catch and manage timer failures.
    
    :param function_name: Callable function to execute.
    :param interval: Interval in milliseconds.
    :param repeating: Boolean indicating if the function should repeat.
    :param depends_on: Timer ID that this timer depends on.
    :return: Timer ID if successful, None if an error occurs.
    """
    try:
        return await SetTimer(function_name, interval, repeating, depends_on)
    except TimerError as e:
        await HandleTimerError(e.timer_id, e.message)
        return None
