__author__ = 'Christopher Nelson'


class Quota:
    def __init__(self, name, maximum_concurrent):
        """
        Creates a new rule enforces a maximum number of globally concurrent jobs in the same
        named queue.

        :param name: The tag name to evaluate.
        :param maximum_concurrent: The maximum number of jobs with this tag that can run at the
            same time.
        """
        self.name = name
        self.maximum_concurrent = maximum_concurrent

    def can_run(self, job, running_jobs):
        """
        Indicate if this job is allowed to run by this rule.

        :param job: The job to test.
        :param running_jobs: A list of currently running jobs.
        :return:
        """
        if self.name not in job.tags:
            return True

        running = [j for j in running_jobs if self.name in j.tags]
        return len(running) < self.maximum_concurrent

    def can_run_on(self, node, job, running_jobs):
        return True

    def satisfied(self, running_jobs):
        """
        This rule is used to determine if another instance of the job should be allocated.

        :param running_jobs: A list of currently running jobs.
        :return: True if the rule is satisfied that enough jobs are running. False if another one should be allocated.
        """
        return True


class Exclude:
    def __init__(self, name, avoid_name):
        """
        Creates a new rule that prohibits this job from running on the same node that another job
        with the avoid tag runs on.

        :param name: The tag name to evaluate.
        :param avoid_name: The tag to avoid.
        """
        self.name = name
        self.avoid_name = avoid_name

    def can_run(self, job, running_jobs):
        """
        Indicate if this job is allowed to run by this rule.

        :param job: The job to test.
        :param running_jobs: A list of currently running jobs.
        :return:
        """
        return True

    def can_run_on(self, node, job, running_jobs):
        """
        If the job is tagged with the name of this rule, and if there are any jobs running on the node
        tagged with the avoid tag then this job will not be allowed to run on this node.

        :param node: The node to check.
        :param job: The job to check.
        :param running_jobs: A list of curently running jobs.
        :return:
        """
        if self.name not in job.tags:
            return True

        running = [j for j in running_jobs if self.avoid_name in j.tags and node in j.nodes]
        return len(running) == 0

    def satisfied(self, running_jobs):
        """
        This rule is used to determine if another instance of the job should be allocated.

        :param running_jobs: A list of currently running jobs.
        :return: True if the rule is satisfied that enough jobs are running. False if another one should be allocated.
        """
        return True
