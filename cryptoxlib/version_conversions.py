import sys
import asyncio
import time


def is_python_version(major: int, minor: int, micro: int = None):
    python_version = sys.version_info
    if python_version.major == major and python_version.minor == minor:
        if micro is not None:
            return python_version.micro == micro
        else:
            return True
    else:
        return False


IS_PYTHON36 = is_python_version(3, 6)
IS_PYTHON37 = is_python_version(3, 7)
IS_PYTHON38 = is_python_version(3, 8)
IS_PYTHON39 = is_python_version(3, 9)


def async_run(f):
    if IS_PYTHON36:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f)
    elif IS_PYTHON37 or IS_PYTHON38 or IS_PYTHON39:
        return asyncio.run(f)

    raise Exception(f'Unsupported Python version! Only versions 3.6.x, 3.7.x and 3.8.x are supported.')


def async_create_task(f):
    if IS_PYTHON36:
        loop = asyncio.get_event_loop()
        return loop.create_task(f)
    elif IS_PYTHON37 or IS_PYTHON38 or IS_PYTHON39:
        return asyncio.create_task(f)

    raise Exception(f'Unsupported Python version! Only versions 3.6.x, 3.7.x and 3.8.x are supported.')


def get_current_time_ms():
    if IS_PYTHON36:
        return time.time() * 1000.0
    else:
        return time.time_ns() / 1000000.0