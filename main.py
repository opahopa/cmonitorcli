#!/usr/bin/env python

from settings.config import *
from version import CLI_VERSION
from client import CmonitorCli

logger = logging.getLogger(__name__)


def main_job():
    logger.info(f"running version: {CLI_VERSION}")
    cclient = CmonitorCli()

    # print("sending status")
    # cclient.send_status()

    # print("calling close")
    # cclient.ws.close()
    pass


if __name__ == "__main__" and __package__ is None:
    __package__ = "client"
    main_job()
