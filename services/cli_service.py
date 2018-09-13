import requests
import logging

from distutils.version import LooseVersion
from settings.config import REST_SERVER
import version

logger = logging.getLogger(__name__)

""""""""""""""""""""""""""""""""""""""""
:returns
:boolean: True if version changed
"""""""""""""""""""""""""""""""""""""""""


def cli_update_watcher():
    try:
        if not version.CLI_VERSION_CHANGED:
            logger.info('Getting current cmoncli version number from API')
            api_cli_version = get_version()['version']
            if LooseVersion(api_cli_version) < LooseVersion(version.CLI_VERSION):
                version.CLI_VERSION_CHANGED = True
                return True
        else:
            return True
    except TypeError:
        logger.error(f'Failed parse version number from API response')
        return False


def get_version():
    try:
        return requests.get(url=REST_SERVER + '/monitor/client/version/', timeout=10).json()
    except Exception as e:
        logger.error(f'Failed to get version number from API {e}')


def generate_cmoncli(token):
    try:
        return requests.get(url=REST_SERVER + '/monitor/client/generate/', timeout=10,
                            headers={'Authorization': f'JWT {token}'}).json()
    except Exception as e:
        logger.error(f'Failed to generate cli {e}')
        return None
