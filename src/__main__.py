import asyncio
from EcmaTimer import SetTimer, KillTimer, HandleTimerError, TimerError

async def example_timer_function():
    print("Timer triggered!")
    
async def main():
    try:
        # Set a simple timer that runs every 2 seconds
        timer_id = await SetTimer(example_timer_function, 2000, repeating=True)

        # Simulate waiting for some time before killing the timer
        await asyncio.sleep(10)

        # Kill the timer after 10 seconds
        await KillTimer(timer_id)
        print("Timer killed after 10 seconds.")
    except TimerError as e:
        await HandleTimerError(e.timer_id, e.message)

if __name__ == "__main__":
    asyncio.run(main())
