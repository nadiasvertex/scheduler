import unittest
from job.rule.limit import Quota, Exclude
from plan.accounting import JobEntry

__author__ = 'Christopher Nelson'


class TestQuota(unittest.TestCase):
    def setUp(self):
        self.running_jobs = [
            JobEntry("process", None, ["dev"]),
            JobEntry("process", None, ["stb"])
        ]

    def test_one(self):
        r = Quota("dev", 1)
        pending_job = JobEntry("publish", None, ["dev"])

        self.assertFalse(r.can_run(pending_job, self.running_jobs))
        self.assertTrue(r.can_run_on("node1", pending_job, self.running_jobs))

    def test_two(self):
        r = Quota("dev", 2)
        pending_job = JobEntry("publish", None, ["dev"])

        self.assertTrue(r.can_run(pending_job, self.running_jobs))
        self.assertTrue(r.can_run_on("node1", pending_job, self.running_jobs))


class TestExclude(unittest.TestCase):
    def setUp(self):
        self.running_jobs = [
            JobEntry("controller", None, ["ceph", "control"], ["node1"]),
            JobEntry("osd", None, ["ceph", "storage"], ["node2"]),
        ]

    def test_works(self):
        r = Exclude("ceph", "storage")
        pending_job = JobEntry("mds", None, ["ceph", "metadata"])

        self.assertTrue(r.can_run(pending_job, self.running_jobs))
        self.assertFalse(r.can_run_on("node2", pending_job, self.running_jobs))
