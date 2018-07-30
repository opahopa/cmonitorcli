#!/usr/bin/env python

from settings.config import *
from client import CmonitorCli

logger = logging.getLogger(__name__)


def main_job():
    cclient = CmonitorCli()

    # print("sending status")
    # cclient.send_status()

    # print("calling close")
    # cclient.ws.close()
    pass


if __name__ == "__main__" and __package__ is None:
    __package__ = "client"
    main_job()
