#!/usr/bin/env python
import os
import sys
import time

from django.db import connections
from django.db.utils import OperationalError


def wait_for_db():
    max_tries = 10
    for i in range(max_tries):
        try:
            connections["default"].cursor()
            return
        except OperationalError:
            print(f"DB not ready, retrying ({i+1}/{max_tries})...")
            time.sleep(3)
    raise Exception("DB not available after several retries")


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    wait_for_db()
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
