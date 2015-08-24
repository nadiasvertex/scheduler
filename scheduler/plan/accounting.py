import logging

from dateutil.parser import parse
from job.rule import limit, availability
from job.schedule import oneshot, periodic

__author__ = 'Christopher Nelson'


class JobEntry:
    def __init__(self, name, schedule, tags=(), nodes=()):
        self.name = name
        self.schedule = schedule
        self.tags = tags

        self.running = False
        self.nodes = list(nodes)

    def add_node(self, node):
        self.nodes.append(node)

    def drop_node(self, node):
        self.nodes.remove(node)


class JobLedger:
    def __init__(self, job_definitions):
        self.log = logging.getLogger(__name__)
        self.job_definitions = job_definitions
        self.job_entries = {}
        self.rules = []

    def _gather_rules(self, definition):
        """
        Gather rules from the job definition. Rules are not merged together, but they are
        gathered into one global list and evaluated for all jobs.

        Invalid rules are logged and skipped.

        :param definition: The job definition to examine.
        """
        def_rules = definition.get("rules", [])
        for rule in def_rules:
            for k, v in rule.items():
                apply_to_tag = v.get("tag", definition["name"])
                if k == "limit":
                    if "quota" not in v and "avoid" not in v:
                        self.log.error(
                            "No limiting terms specified in limit rule for job '%s'. (Use quota or avoid.)",
                            definition["name"]
                        )
                        continue

                    if "quota" in v:
                        self.rules.append(limit.Quota(apply_to_tag, v["quota"]))

                    if "avoid" in v:
                        self.rules.append(limit.Exclude(apply_to_tag, v["avoid"]))

                elif k == "availability":
                    self.rules.append(availability.Replicate(apply_to_tag, v.get("instances", 1)))

    def _parse_schedules(self, schedules):
        rv = []
        for k, v in schedules.items():
            if k == "periodic":
                rv.append()
            elif k == "oneshot":
                when = parse(v.get("at"))
                rv.append(oneshot.OneShot(when))

        return rv

    def _create_job_entry(self, name, node):
        d = self.job_definitions.get(name)
        if d is None:
            return None

        n = d["name"]
        return JobEntry(n, None, [node], d.get("tags", []) + [n])

    def add_job(self, node, queue, queue_name):
        """
        Adds a job to the ledger. If a job with the given name already exists it will be merged with
        the existing job. Rules from the job are collected together with existing rules to form a global
        rule set.

        :param definition: The job definition to examine.
        """
        # self._gather_rules(definition)
        # name = definition["name"]
        for name in queue:
            job = self.job_entries.get(name, self._create_job_entry(name))
            if job is None:
                self.log.error("No job definition for queued job '%s' in queue '%s'", name, queue_name)
                continue
