from subprocess import PIPE, run, CalledProcessError


class SystemService(object):


    def get_hostname(self):
        try:
            result = run(['uname', '-n'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
            return result.returncode, result.stdout.strip(), result.stderr
        except CalledProcessError as e:
            output = e.output.decode()
            print(output)


    def check_all(self):
        pass