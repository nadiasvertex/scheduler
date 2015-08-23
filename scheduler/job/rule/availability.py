__author__ = 'Christopher Nelson'


class Available:
    def __init__(self, name, required_concurrent):
        """
        Creates a new rule that requires a job to run on multiple nodes. The rule requires
        that the job run on different nodes.

        :param name: The tag name to evaluate.
        :param required_concurrent: The number of jobs that must run concurrently for this rule to
            be satisfied.
        """

        self.name = name
        self.required_concurrent = required_concurrent

    def can_run(self, job, running_jobs):
        """
        Indicate if this job is allowed to run by this rule.

        :param job: The job to test.
        :param running_jobs: A list of currently running jobs.
        :return:
        """
        if self.name not in job.tags:
            return True

        running = [len(j.nodes) for j in running_jobs if self.name in j.tags]
        return sum(running) < self.required_concurrent


    def can_run_on(self, node, job, running_jobs):
        """running = [j for j in running_jobs if self.name in j.tags]
        Indicate if this job can run on this node.

        :param node: The node to check.
        :param job: The job to check.
        :param running_jobs: A list of currently running jobs.
        """
        if self.name not in job.tags:
            return True

        running = [j for j in running_jobs if self.name in j.tags and node in j.nodes]
        return len(running) == 0

    def satisfied(self, running_jobs):
        """
        This rule is used to determine if another instance of the job should be allocated.

        :param running_jobs: A list of currently running jobs.
        :return: True if the rule is satisfied that enough jobs are running. False if another one should be allocated.
        """
        running = [len(j.nodes) for j in running_jobs if self.name in j.tags]
        return sum(running) == self.required_concurrent

