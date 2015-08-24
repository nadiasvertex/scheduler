from datetime import datetime

__author__ = 'Christopher Nelson'


class Periodic:
    def __init__(self, minute=range(60), hour=range(24), day_of_week=range(7), day_of_month=range(1, 32),
                 month=range(1, 13)):
        """
        Create a periodically recurring job. The parameters are iterables containing the valid values for
        the various items. The values must be sorted from lowest to highest.

        :param minute: The minutes of the hour the job should run.
        :param hour: The hours of the day the job should run.
        :param day_of_week: The days of the week the job should run.
        :param day_of_month: The days of the month the job should run.
        """
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.month = month

    def _get_next_item(self, r, partition):
        """
        Get the next item in the range.

        :param r: The range.
        :param partition: The value that the return value must be larger than.
        :return: A value larger than partition, or None if you must wrap.
        """
        if r is None:
            return partition + 1

        available = [v for v in r if v > partition]
        if not available:
            return None

        return available[0]

    def _increment(self, limit, potential, i, r):
        """
        Performs increment with wrapping and reset.

        :param limit: The limit array for the items.
        :param potential: The potential values to set.
        :param i: The index of the value to increment.
        :param r: The range for the value to increment.
        """
        # Reset all items AFTER this to their minimum.
        for j in range(i + 1, len(limit)):
            potential[j] = min(limit[j])

        # Increment with rollover this item and all PREVIOUS
        # as necessary.
        for wrap_i in range(i, -1, -1):
            potential[wrap_i] = self._get_next_item(limit[wrap_i], potential[wrap_i])
            if potential[wrap_i] is not None:
                break

            # Reset this item to its minimum because it exceeded its
            # range. This will cause us to loop to the next larger item
            # and bump it to its next valid size or wrap.
            potential[wrap_i] = min(r)

    @staticmethod
    def _parse_range_component(r, default):
        if "," in r:
            return Periodic._parse_range(r.split(","), default)

        major = r.split("/")
        interval = int(major[1]) if len(major) == 2 else 1

        minor = major[0].strip()
        if minor.startswith("-"):
            return range(min(default), int(minor[1:]) + 1, interval)
        elif minor.endswith("-"):
            return range(int(minor[0:-1]), max(default) + 1, interval)
        elif "-" in minor:
            minor = minor.split("-")
            return range(int(minor[0]), int(minor[1]) + 1, interval)
        elif interval > 1:
            return range(min(default), max(default) + 1, interval)
        else:
            return [int(minor)]

    @staticmethod
    def _parse_range(r, default):
        if type(r) is int:
            return [r]

        if type(r) is str:
            return Periodic._parse_range_component(r, default)

        # Expand the list items so that any mix of integers and strings yields the largest
        # intersection of possible values.
        if type(r) is list:
            o = set()
            for item in r:
                ti = type(item)
                if ti is int:
                    o.add(item)
                elif ti is str:
                    for n in Periodic._parse_range(item, default):
                        o.add(n)

            return sorted(o)

    @staticmethod
    def from_json(v):
        return Periodic(
            Periodic._parse_range(v.get("minute"), range(0, 60)),
            Periodic._parse_range(v.get("hour"), range(0, 24)),
            Periodic._parse_range(v.get("day_of_week"), range(0, 7)),
            Periodic._parse_range(v.get("day_of_month"), range(1, 32)),
            Periodic._parse_range(v.get("month"), range(1, 13))
        )

    def get_next_deadline(self, now=datetime.now()):
        """
        Finds the next absolute point in time when it is valid to schedule this item. Note that this
        function might return a value equivalent to now, which means that the job should be run
        immediately.

        :param now: The moment from which we should calculate the deadline. Defaults to datetime.now().
        :return: A datetime indicating the next deadline for this schedule.
        """

        potential = [now.year, now.month, now.day, now.hour, now.minute]
        limit = [None, self.month, self.day_of_month, self.hour, self.minute]

        for i, r in enumerate(limit):
            if r is None:
                continue

            value = potential[i]
            if value in r:
                continue

            # We need to bump the value in this slot, which means
            # wrapping. Wrapping is very complicated because we
            # may need to wrap all elements BEFORE the current
            # one if they all spill. In addition, we must reset
            # to the minimum any elements AFTER the current one
            # regardless of what else we do.

            self._increment(limit, potential, i, r)

            # In all cases, once the preceding loop has executed the entire
            # projected date is now valid. This is because wrapping forces
            # all future items into valid ranges.
            break

        # Evaluate the day of week restriction.
        while True:
            d = datetime(*potential)
            if d.weekday() in self.day_of_week:
                return d

            self._increment(limit, potential, 2, self.day_of_month)
