import unittest
from job.rule.availability import Replicate
from job.rule.limit import Quota
from plan.accounting import JobEntry

__author__ = 'Christopher Nelson'


class TestAvailability(unittest.TestCase):
    def setUp(self):
        self.running_jobs = [
            JobEntry("publisher", None, ["dev-publisher"], ["node1"]),
            JobEntry("publisher", None, ["stb-publisher"], ["node2", "node1"])
        ]

    def test_one_satisifed(self):
        r = Replicate("dev-publisher", 1)
        pending_job = self.running_jobs[0]

        self.assertFalse(r.can_run(pending_job, self.running_jobs))
        self.assertTrue(r.can_run_on("node2", pending_job, self.running_jobs))
        self.assertTrue(r.satisfied(self.running_jobs))

    def test_two_unsatisfied(self):
        r = Replicate("dev-publisher", 2)
        pending_job = self.running_jobs[0]

        self.assertTrue(r.can_run(pending_job, self.running_jobs))
        self.assertFalse(r.can_run_on("node1", pending_job, self.running_jobs))
        self.assertTrue(r.can_run_on("node2", pending_job, self.running_jobs))
        self.assertFalse(r.satisfied(self.running_jobs))

        pending_job.add_node("node2")
        self.assertTrue(r.satisfied(self.running_jobs))

    def test_two_satisfied(self):
        r = Replicate("stb-publisher", 2)
        pending_job = self.running_jobs[1]

        self.assertFalse(r.can_run(pending_job, self.running_jobs))
        self.assertFalse(r.can_run_on("node1", pending_job, self.running_jobs))
        self.assertFalse(r.can_run_on("node2", pending_job, self.running_jobs))
        self.assertTrue(r.satisfied(self.running_jobs))

        pending_job.drop_node("node2")
        self.assertFalse(r.satisfied(self.running_jobs))
