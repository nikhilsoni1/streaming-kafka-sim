from contextlib import contextmanager
from time import perf_counter
from render_rig2.utils.logger import logger
from render_rig2.utils.logger import is_debug_enabled


@contextmanager
def timed_debug_log(message: str):
    if is_debug_enabled():
        start = perf_counter()
        yield
        duration = round(perf_counter() - start, 2)
        logger.debug(f"{message} took {duration}s")
    else:
        yield
