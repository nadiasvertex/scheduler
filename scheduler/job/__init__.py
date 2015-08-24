__author__ = 'Christopher Nelson'


# A job definition is a dictionary that looks like this:
_ = \
    {
        "name": "job_name",
        "tags": ["a", "list", "of", "tags"],
        "type": "service | batch",
        "execution": {
            "command": ["some_command", "arg1", "arg2", "arg3"],
            "working_directory": "/path/to/some/dir",
            "run_as": "some_user"
        },

        "schedule": [
            {
                # All values are optional. If the value is missing it means every value. A number
                # of options are shown below. Note that a list can contain strings and integers.
                # Any redundancies will be eliminated by the parser.
                "periodic": {
                    "month": [1, 2, 3],  # A list of numbers specifies these values and no others.
                    "day_of_month": ["1-5", "15-20"],  # A list of strings can be ranges.
                    "day_of_week": 0,  # A single number means that one value.
                    "hour": ["1-12/2, 11-23"],  # A list of strings can also have ranges and intervals
                    "minute": "/5", # A string can contain just an interval. In this case, every 5 minutes.
                },

                "oneshot" : {
                    "at": "January 5, 2020 12:56pm"
                }
            }
        ],

        # For rules, the tag parameter is optional. If not specified it will
        # default to the job name.
        "rules": [
            {"limit": {"tag": "name", "quota": 1, "avoid": ["some", "tags"]}},
            {"availability": {"tag": "name", "instances": 3}},
        ]

    }
