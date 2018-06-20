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

class ReportDaemon(object):

    def __init__(self, status, message, runtime):
        """single service report."""
        self.type = "service"
        self.status = status
        self.message = message
        self.runtime = runtime

    def to_json(self):
        pass