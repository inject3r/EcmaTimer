import unittest
import asyncio
from unittest.mock import AsyncMock
from EcmaTimer import *

class TestEcmaTimer(unittest.TestCase):

    def setUp(self):
        """Setup method for initializing necessary components before each test"""
        global timers, timer_counter, set_timer_count, set_timer_ex_count, priority_queue, timer_dependencies
        timers = {}
        timer_counter = 1
        set_timer_count = 0
        set_timer_ex_count = 0
        priority_queue = PriorityQueue()
        timer_dependencies = {}

    def test_SetTimer_valid(self):
        """Test SetTimer with a valid function and interval"""
        async def mock_function():
            pass

        # Set a valid timer
        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=False))

        # Check if the timer is created in the timers dictionary
        self.assertIn(timer_id, timers)
        self.assertEqual(timers[timer_id]['function_name'], mock_function)
        self.assertFalse(timers[timer_id]['repeating'])

    def test_SetTimer_invalid_function(self):
        """Test SetTimer with an invalid function"""
        with self.assertRaises(InvalidFunctionError):
            asyncio.run(SetTimer(None, 1000, repeating=False))

    def test_SetTimer_invalid_interval(self):
        """Test SetTimer with an invalid interval"""
        async def mock_function():
            pass
        
        with self.assertRaises(InvalidIntervalError):
            asyncio.run(SetTimer(mock_function, -1, repeating=False))

    def test_KillTimer_valid(self):
        """Test KillTimer for a valid timer"""
        async def mock_function():
            pass

        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=False))
        result = asyncio.run(KillTimer(timer_id))
        
        # Ensure the timer is removed from the timers
        self.assertEqual(result, 0)
        self.assertNotIn(timer_id, timers)

    def test_KillTimer_invalid(self):
        """Test KillTimer for an invalid timer ID"""
        with self.assertRaises(TimerNotFoundError):
            asyncio.run(KillTimer(999))

    def test_SetTimer_with_dependencies(self):
        """Test SetTimer with dependencies"""
        async def mock_function_1():
            pass

        async def mock_function_2():
            pass

        timer_id_1 = asyncio.run(SetTimer(mock_function_1, 1000, repeating=False))
        timer_id_2 = asyncio.run(SetTimer(mock_function_2, 1000, repeating=False, depends_on=timer_id_1))

        # Ensure the dependent timer is registered correctly
        self.assertIn(timer_id_2, timers)
        self.assertEqual(timers[timer_id_2]['depends_on'], timer_id_1)

    def test_SetTimerEx_valid(self):
        """Test SetTimerEx with valid parameters"""
        async def mock_function(arg):
            pass

        timer_id = asyncio.run(SetTimerEx(mock_function, 1000, repeating=False, 1))
        self.assertIn(timer_id, timers)
        self.assertEqual(timers[timer_id]['function_name'], mock_function)

    def test_SetTimerEx_invalid_function(self):
        """Test SetTimerEx with an invalid function"""
        with self.assertRaises(InvalidFunctionError):
            asyncio.run(SetTimerEx(None, 1000, repeating=False))

    def test_SetTimerEx_invalid_interval(self):
        """Test SetTimerEx with an invalid interval"""
        async def mock_function(arg):
            pass

        with self.assertRaises(InvalidIntervalError):
            asyncio.run(SetTimerEx(mock_function, -1, repeating=False, 1))

    def test_PauseTimer_and_ResumeTimer(self):
        """Test PauseTimer and ResumeTimer"""
        async def mock_function():
            pass

        # Set a timer
        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=False))
        
        # Pause the timer
        asyncio.run(PauseTimer(timer_id))
        self.assertIn('remaining_time', timers[timer_id])
        
        # Resume the timer
        asyncio.run(ResumeTimer(timer_id))
        self.assertNotIn('remaining_time', timers[timer_id])

    def test_SetTimerWithPriority(self):
        """Test SetTimer with priority handling"""
        async def mock_function():
            pass

        timer_id = asyncio.run(SetTimerWithPriority(mock_function, 1000, repeating=False, priority=1))
        self.assertIn(timer_id, timers)
        self.assertEqual(timers[timer_id]['priority'], 1)

    def test_SetCancelableTimer(self):
        """Test SetCancelableTimer functionality"""
        async def mock_function():
            pass

        timer_id = asyncio.run(SetCancelableTimer(mock_function, 1000, repeating=False))
        self.assertIn(timer_id, timers)
        self.assertTrue(timers[timer_id].get('cancelable', False))

    def test_HandleTimerError(self):
        """Test the error handling in a timer"""
        async def mock_function():
            raise Exception("Mock Error")

        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=False))

        # Ensure the error is handled correctly
        with self.assertRaises(TimerError):
            asyncio.run(KillTimer(timer_id))  # Triggering the error handling in KillTimer

    def test_IsValidTimer(self):
        """Test IsValidTimer for checking if a timer exists"""
        async def mock_function():
            pass

        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=False))
        self.assertTrue(IsValidTimer(timer_id))

    def test_IsRepeatingTimer(self):
        """Test IsRepeatingTimer for checking if a timer is repeating"""
        async def mock_function():
            pass

        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=True))
        self.assertTrue(IsRepeatingTimer(timer_id))

    def test_CountRunningTimers(self):
        """Test CountRunningTimers to count the active timers"""
        async def mock_function():
            pass

        timer_id = asyncio.run(SetTimer(mock_function, 1000, repeating=False))
        self.assertEqual(CountRunningTimers(), 1)

        asyncio.run(KillTimer(timer_id))
        self.assertEqual(CountRunningTimers(), 0)

if __name__ == '__main__':
    unittest.main()
