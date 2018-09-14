import logging
import os, sys
import json

from services.system.system_service import SystemService
from settings.config import bundle_dir

logger = logging.getLogger(__name__)

if getattr(sys, 'freeze', False):
    # running as bundle (aka frozen)
    bundle_dir = sys._MEIPASS
else:
    # running live
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


def bash_cmd_result(result):
    try:
        if hasattr(result, 'stdout') and result.stdout and result.returncode == 0:
            return {'success': True, 'body': result.stdout.strip()}
        if hasattr(result, 'stderr') and result.stderr:
            if result.stdout:
                err = '\n' + result.stdout + '\n' + result.stderr
            else:
                err = result.stderr
        else:
            err = result
        return {'success': False, 'body': f"Run bash script command execution error. {err}"}
    except Exception as e:
        logger.error(f'bash script cmd result parsing error: {e}')
        return {'success': False, 'body': f"bash script cmd result parsing error: {err}"}


""""""""""""""""""""""""""""""""""""""""
:returns
dictionary:

:success: boolean
:body: string
"""""""""""""""""""""""""""""""""""""""""
def run_bash_script(script_path, command=None):
    try:
        with SystemService() as system_service:

            if command is None:
                command = f"bash {os.path.join(bundle_dir, script_path)}"

            logger.info("Running run_bash_script(), command: {}".format(command))
            result = system_service.run_command(command, shell=True, timeout=45)
            return bash_cmd_result(result)
    except Exception as e:
        logger.error(e)
        return {'success': False, 'body': e}

