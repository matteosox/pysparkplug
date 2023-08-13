"""Module of time utilties"""

import time

__all__ = ["get_current_timestamp"]


def get_current_timestamp() -> int:
    """Returns current time in a Sparkplug B compliant format"""
    return int(time.time() * 1e3)
