from loguru import logger
import sys
import os
import inspect
from functools import wraps

def setup_logger(log_file_path=None):
    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", serialize=True, level="INFO")
    if log_file_path:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        logger.add(log_file_path, serialize=True, level="INFO")
    return logger

def log_function(log_return: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            arg_names = inspect.getfullargspec(func).args
            arg_str = ', '.join(f"{name}={value!r}" for name, value in zip(arg_names, args))
            kwarg_str = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
            signature = ", ".join(filter(None, [arg_str, kwarg_str]))

            logger.info(f"▶️ Enter: {func_name}({signature})")
            try:
                result = func(*args, **kwargs)
                if log_return:
                    logger.info(f"✅ Exit: {func_name} -> {result!r}")
                else:
                    logger.info(f"✅ Exit: {func_name}")
                return result
            except Exception as e:
                logger.exception(f"❌ Exception in {func_name}: {e}")
                raise
        return wrapper
    return decorator
