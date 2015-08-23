__author__ = 'Christopher Nelson'

# A job definition is a dictionary that looks like this:
{
    "name": "job_name",
    "tags": ["a", "list", "of", "tags"],
    "type": "service | batch",
    "execution": {
        "command": ["some_command", "arg1", "arg2", "arg3"],
        "working_directory": "/path/to/some/dir",
        "run_as": "some_user"
    },
    "rules": {
        "quota": {"tag": "name", "limit": 1},
        "availability": {"tag": "name", "instances": 3}
    }

}
