from functools import wraps
from time import time
import logging
from typing import Union

def get_default_logger():
    return MyLogger().get_logger()

class MyLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

    def get_logger(self, name=None):
        return logging.getLogger(name)

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        logger = get_default_logger()
        ts = time()
        result = f(*args, **kw)
        te = time()
        logger.info('func:%r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return wrap

def log(_func=None, *, my_logger: Union[MyLogger, logging.Logger] = None):
    def decorator_log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_default_logger()
            try:
                if my_logger is None:
                    first_args = next(iter(args), None)  # capture first arg to check for `self`
                    logger_params = [  # does kwargs have any logger
                        x
                        for x in kwargs.values()
                        if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                    ] + [  # # does args have any logger
                        x
                        for x in args
                        if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                    ]
                    if hasattr(first_args, "__dict__"):  # is first argument `self`
                        logger_params = logger_params + [
                            x
                            for x in first_args.__dict__.values()  # does class (dict) members have any logger
                            if isinstance(x, logging.Logger)
                            or isinstance(x, MyLogger)
                        ]
                    h_logger = next(iter(logger_params), MyLogger())  # get the next/first/default logger
                else:
                    h_logger = my_logger  # logger is passed explicitly to the decorator

                if isinstance(h_logger, MyLogger):
                    logger = h_logger.get_logger(func.__name__)
                else:
                    logger = h_logger

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                logger.debug(f"function {func.__name__} called with args {signature}")
            except Exception:
                pass

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)