'''
The scheduler is a distributed scheduling service. It can run batch jobs or services. The system uses simple algorithms
and is not designed for large clusters. Think of it as a distributed cron job with the ability to manage long-running
processes too.

The structure is simple. An instance of the scheduler runs on every node that can run jobs. There is a leader which
decides when items should be scheduled. The scheduler uses Consul for configuration and leader election. It also
registers services it runs with Consul.

The scheduler maintains a work queue for every node in the system. Jobs scheduled in the system can have tags applied
to them. The tags do not mean anything to the scheduler. However, in addition to timing, jobs can also have restrictions
applied to them. For example, if any running job in the system has a particular tag the scheduler can hold new jobs
with the same tag until the currently running job finishes.

'''

