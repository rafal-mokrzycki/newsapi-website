import logging
import random
import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time() - t1
        logging.info(f"`{func.__name__}` ran in {t2} seconds")
        return result

    return wrapper


def wait_for_web_scraping():
    time.sleep(random.randint(5, 10))
