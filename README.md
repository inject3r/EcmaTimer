# EcmaTimer

[![PyPI version](https://img.shields.io/pypi/v/EcmaTimer.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/EcmaTimer)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/EcmaTimer.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/EcmaTimer)
[![PyPI downloads](https://img.shields.io/pypi/dm/ecmatimer.svg)](https://pypistats.org/packages/ecmatimer)
[![GitHub Actions status](https://github.com/inject3r/EcmaTimer/workflows/Test/badge.svg)](https://github.com/inject3r/EcmaTimer/actions)
[![Licence](https://img.shields.io/github/license/inject3r/EcmaTimer.svg)](COPYING.txt)
[![Code style: Black](https://img.shields.io/badge/code%20style-Black-000000.svg)](https://github.com/psf/black)

## Installation

### From PyPI

```bash
python3 -m pip install --upgrade EcmaTimer
```

### From source

```bash
git clone https://github.com/inject3r/EcmaTimer.git
cd EcmaTimer
python3 -m pip install .
```

## Example

```python
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
```

## Features

- **Asynchronous timers** using `asyncio`.
- **Repeating and one-shot timers**.
- **Exception handling** for timer errors.
- **Easy integration** into async Python applications.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Issues

If you find a bug or want to request a feature, please open an issue on [GitHub](https://github.com/inject3r/EcmaTimer/issues).
(ـ
