import logging
from typing import List

import botocore
import urllib3

from datetime import time

from utils.logging import LoggingUtils

log = LoggingUtils.configure_logging(__name__)

BACKOFF = .25
MAX_RETRIES = 10


class Utils:
    @staticmethod
    def trace(func):
        def wrapper(*args, **kwargs):
            log.info(f"Entering function: {func.__name__} with args: {args}")
            result = func(*args, **kwargs)
            # log.info(f"Returning result: {result}")
            log.info(f"Exiting function: {func.__name__}")
            return result

        return wrapper

    @staticmethod
    def retry(function):
        """
        Decorator that supports automatic retries if connectivity issues are detected with boto or urllib operations
        """

        def inner(self, *args, **kwargs):
            retries = 0
            while True:
                try:
                    return function(self, *args, **kwargs)
                except (botocore.exceptions.EndpointConnectionError, urllib3.exceptions.NewConnectionError) as e:
                    if retries > MAX_RETRIES:
                        raise e

                    self._utils.notify("Network connectivity issues detected. Retrying with back off...")
                    retries += 1
                    time.sleep(retries * BACKOFF)

        return inner

    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    @staticmethod
    def validate(self, boolean: bool, error_msg: str):
        if not boolean:
            raise ValueError(error_msg)
