from datetime import datetime

__author__ = 'Christopher Nelson'


class OneShot:
    def __init__(self, target, cancel_if_missed=False):
        """
        Create a job intended to run once.

        :param target: A datetime object indicating when the job should run next.
        :param cancel_if_missed: If the specified target time has already passed and this parameter is set to True, the
                                 schedule object will indicate that the job should cancelled. The default behavior is
                                 to make up the job.
        """
        self.has_run = False
        self.cancel_if_missed = cancel_if_missed
        self.deadline = target


    def get_next_deadline(self, now=datetime.now()):
        """
        Finds the next absolute point in time when it is valid to schedule this item. This function
        may return a copy of now, indicating the the job should be scheduled immediately.

        :param now: The moment from which we should calculate the deadline. Defaults to datetime.now().
        :return: A datetime indicating the next deadline for this schedule, or None indicating that it
                 should never run again.
        """
        if self.has_run:
            return None

        if now > self.deadline and self.cancel_if_missed:
            return None

        self.has_run = True
        return datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
