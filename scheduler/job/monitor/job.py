import logging
import os
import socket
import subprocess
import pwd

__author__ = 'Christopher Nelson'


class Job:
    def __init__(self, name, command, cwd=None, env=None, replace_env=False,
                 std_out_path=None, std_err_path=None, run_as=None):
        """
        Creates a new job monitor.

        :param command: A list containing the command and arguments to run.
        :param cwd: The current working directory to set for the process before running it.
        :param env: If present, it must be a dictionary of variables to set for the child's environment. These will
                    be added to (or overwrite) variables existing in the parent's process.
        :param replace_env: If set to True and env is present, the environment will completely replace the child's
                    environment when run.
        :param std_out_path: The path to the file where the job's standard output should be written. If None, the
            default location is /var/log/scheduler/<name>.out.log
        :param std_err_path: The path to the file where the job's standard error should be written. If None, the
            default location is /var/log/scheduler/<name>.err.log
        :param run_as: The username to run the job as. The scheduler must be running as root in order to provide
            this facility.
        :param tags: Tags applied to the job.
        """
        self.log = logging.getLogger(__name__ + "/" + name)

        self.name = name
        self.command = command
        self.cwd = cwd
        self.env = env
        self.replace_env = replace_env

        std_base = os.path.join("/var", "log", "scheduler")
        self.std_out_path = os.path.join(std_base, self.name + ".out.log") \
            if std_out_path is None else std_out_path
        self.std_err_path = os.path.join(std_base, self.name + ".err.log") \
            if std_err_path is None else std_err_path
        self.run_as = run_as

        self.p = None
        self.std_out = None
        self.std_err = None

        self.log.debug("job monitor '%s' created for '%s'", name, " ".join(command))

    def _ensure_folder_exists(self, folder):
        if not os.path.exists(folder):
            self.log.debug("creating folder '%s'", folder)
            os.makedirs(folder)

    def run(self):
        self.log.debug("running job '%s' on '%s'", self.name, socket.gethostname())

        self._ensure_folder_exists(os.path.dirname(self.std_out_path))
        self._ensure_folder_exists(os.path.dirname(self.std_err_path))

        if self.run_as is not None:
            pwe = pwd.getpwnam(self.run_as)
            user_name = pwe.pw_name
            user_home_dir = pwe.pw_dir
            user_uid = pwe.pw_uid
            user_gid = pwe.pw_gid

            run_as_environment = {
                "HOME": user_home_dir,
                "LOGNAME": user_name,
                "USER": user_name
            }

            self.log.debug("running as user '%s'", user_name)

        else:
            run_as_environment = None

        # Prepare the environment, keeping in mind the run_as environment.
        if self.env is not None or run_as_environment is not None:
            environment = os.environ.copy() if not self.replace_env else {}

            if run_as_environment is not None:
                environment.update(run_as_environment)

            if self.env is not None:
                environment.update(self.env)
        else:
            environment = None

        if self.std_out is None:
            self.std_out = open(self.std_out_path, "a")

        if self.std_err is None:
            self.std_err = open(self.std_err_path, "a")

        def pre_exec():
            os.setgid(user_gid)
            os.setuid(user_uid)

        self.p = subprocess.Popen(
            self.command, stdout=self.std_out, stderr=self.std_err, cwd=self.cwd, env=environment,
            preexec_fn=None if self.run_as is None else pre_exec
        )

        self.log.debug("created new child process %d", self.p.pid)

    def is_running(self):
        if self.p is None:
            return False

        return self.p.poll() is None

    def close(self):
        if self.p is not None:
            if self.p.poll() is None:
                self.log.debug("terminating process %d", self.p.pid)
                self.p.terminate()
                try:
                    self.p.wait(30)
                except subprocess.TimeoutExpired:
                    self.log.warning("Process %d failed to terminate, sending kill signal.", self.p.pid)
                    self.p.kill()

            self.p = None

        if self.std_out is not None:
            self.std_out.close()
            self.std_out = None
        if self.std_err_path is not None:
            self.std_err.close()
            self.std_err = None
