from settings.logging import *

from services.system.system_service import SystemService

if __name__ == '__main__':
    with SystemService() as system_service:
        system_service.report_all()