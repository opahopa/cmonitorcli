import requests
import logging

from models.message import MessageCommands, MessageStatus
from distutils.version import LooseVersion
from settings.config import REST_SERVER
import version

logger = logging.getLogger(__name__)


def cli_update_request(hostname):
    if cli_update_watcher() is True:
        msg = {
            'type': "REPORT",
            'command': MessageCommands.CLI_UPGRADE_REQUIRED,
            'status': MessageStatus.OK.name,
            'hostname': hostname
        }
        return msg
    else:
        return None


""""""""""""""""""""""""""""""""""""""""
:returns
:boolean: True if version changed
"""""""""""""""""""""""""""""""""""""""""

def cli_update_watcher():
    try:
        if not version.CLI_VERSION_CHANGED:
            logger.info('Getting current cmoncli version number from API')
            api_cli_version = get_version()['version']
            if LooseVersion(version.CLI_VERSION) < LooseVersion(api_cli_version):
                version.CLI_VERSION_CHANGED = True
                logger.info('cmoncli version changed')
                return True
        else:
            return True
    except TypeError:
        logger.error(f'Failed parse version number from API response')
        return False


def get_version():
    try:
        return requests.get(url=REST_SERVER + '/monitor/client/info/version/', timeout=10).json()
    except Exception as e:
        logger.error(f'Failed to get version number from API {e}')


def generate_cmoncli(token):
    try:
        logger.info(REST_SERVER)
        return requests.get(url=REST_SERVER + '/monitor/client/generate/', timeout=10,
                            headers={'Authorization': f'JWT {token}'}).json()
    except Exception as e:
        logger.error(f'Failed to generate cli {e}')
        return None
