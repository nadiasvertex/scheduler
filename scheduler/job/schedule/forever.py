
from datetime import datetime

__author__ = 'Christopher Nelson'


class Forever:
    def __init__(self):
        """
        Create a job intended to run forever.
        """
        pass

    def get_next_deadline(self, now=datetime.now()):
        """
        Finds the next absolute point in time when it is valid to schedule this item. This function
        will return a copy of now, indicating the the job should be scheduled immediately.

        :param now: The moment from which we should calculate the deadline. Defaults to datetime.now().
        :return: A datetime indicating the next deadline for this schedule.
        """
        return datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
