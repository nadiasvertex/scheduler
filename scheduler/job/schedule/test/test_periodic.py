from datetime import datetime
import unittest

from job.schedule.periodic import Periodic

__author__ = 'Christopher Nelson'


class TestPeriodical(unittest.TestCase):
    def test_simple(self):
        p = Periodic()

        now = datetime.now()
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(now.year, now.month, now.day, now.hour, now.minute))

    def test_wrap_and_reset(self):
        p = Periodic(hour=[0, 12])

        now = datetime(2000, 10, 5, 3, 43, 1)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 10, 5, 12))


    def test_hourly(self):
        p = Periodic(hour=[0, 12])

        now = datetime(2000, 10, 5, 3)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 10, 5, 12))

        now = datetime(2000, 10, 5, 13)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 10, 6))

    def test_daily(self):
        p = Periodic(day_of_month=range(1,31,2))

        now = datetime(2000, 10, 5)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 10, 5))

        now = datetime(2000, 10, 6)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 10, 7))

    def test_day_of_week(self):
        p = Periodic(day_of_week=[2, 4])

        now = datetime(2015, 8, 22)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2015, 8, 26))

        now = datetime(2015, 8, 27)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2015, 8, 28))


    def test_monthly(self):
        p = Periodic(month=[4,8,12])

        now = datetime(2000, 10, 1)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 12, 1))

        now = datetime(2000, 3, 1)
        next_deadline = p.get_next_deadline(now)

        self.assertEqual(next_deadline, datetime(2000, 4, 1))
