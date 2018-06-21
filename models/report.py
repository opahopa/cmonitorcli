import json


class ReportAll(object):
    def __str__(self, *args, **kwargs):
        return ""

    def __init__(self, status, services, serv_runtime):
        """
            main report containing array ReportService.
            self.services = list of ReportService
        """
        self.type = "main"
        self.services = services
        self.serv_runtime = serv_runtime

    def to_json(self):
        pass


class ReportService(object):

    def __init__(self, active, name, last_log=None, runtime=None, warning=None):
        """single service report."""
        self.type = "service"
        self.active = active
        self.name = name
        self.last_log = last_log
        self.runtime = runtime
        self.warning = warning

    def toDict(self):
        return {
            'type': self.type,
            'active': self.active,
            'name': self.name,
            'last_log': self.last_log,
            'runtime': self.runtime,
            'warning': self.warning
        }

    def to_json(self):
        pass
