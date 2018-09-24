import logging
import os, sys
import json

from services.system.system_service import SystemService
from settings.config import bundle_dir
from services.utils import Dict2Obj
from services.utils import set_fee_in_codiusconf, set_variables_in_codiusconf
from models.codius_vars import CodiusVariables

logger = logging.getLogger(__name__)

if getattr(sys, 'freeze', False):
    # running as bundle (aka frozen)
    bundle_dir = sys._MEIPASS
else:
    # running live
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


def bash_cmd_result(result, exclude_errors=False):
    try:
        err = None
        if isinstance(result, Dict2Obj):
            if len(result.stdout) > 1 and result.returncode == 0:
                if len(result.stderr) > 1:
                    return {'success': True, 'body': result.stderr + result.stdout.strip()}
                return {'success': True, 'body': result.stdout.strip()}
            if len(result.stdout) > 1 and result.returncode != 0:
                if len(result.stderr) > 1:
                    return {'success': True, 'body': result.stderr + result.stdout.strip()}
                return {'success': True, 'body': result.stdout.strip()}
            if len(result.stderr) > 1:
                try:
                    err = '\n' + result.stderr + '\n' + result.stdout
                except:
                    err = result.stderr

            if not err:
                err = result.__dict__
        else:
            err = result

        return {'success': False, 'body': f"Run bash script command execution error. {err}"}
    except Exception as e:
        logger.error(f'bash script cmd result parsing error: {e}')
        return {'success': False, 'body': f"bash script cmd result parsing error: {e}"}


""""""""""""""""""""""""""""""""""""""""
:parameter cmd_args[]: optional bash script arguments

:returns
dictionary:

:success: boolean
:body: string
"""""""""""""""""""""""""""""""""""""""""


def run_bash_script(script_path, command=None, timeout=None, cmd_args=None):
    try:
        with SystemService() as system_service:

            if command is None:
                command = f"bash {os.path.join(bundle_dir, script_path)}"

            if cmd_args and len(cmd_args) > 0:
                command = command + " " + " ".join([str(a) for a in cmd_args])

            logger.info("Running run_bash_script(), command: {}".format(command))
            if timeout == None:
                timeout = 45
            result = system_service.run_command(command, shell=True, timeout=timeout)
            return bash_cmd_result(result)
    except Exception as e:
        logger.error(e)
        return {'success': False, 'body': e}


def set_codiusd_fee(fee):
    with SystemService() as system_service:
        result = set_fee_in_codiusconf(fee)
        system_service.run_command('systemctl daemon-reload', shell=True)
        system_service.run_command('systemctl restart codiusd', shell=True)
        return result


def set_codiusd_variables(vars):
    if len(vars) > 0:
        for v in vars:
            try:
                if CodiusVariables.has_value(v['name']):
                    return {'success': False, 'body': 'Invalid variable names'}
                else:
                    with SystemService() as system_service:
                        result = set_variables_in_codiusconf(vars)
                        system_service.run_command('systemctl daemon-reload', shell=True)
                        system_service.run_command('systemctl restart codiusd', shell=True)
                        return result
            except Exception as e:
                logger.info(e)
                return {'success': False, 'body': e}
    return {'success': False, 'body': 'No codiusd variables to set'}


def hyperd_rm_pods(data):
    if len(data['pods']) > 0 or data['all']:
        with SystemService() as system_service:
            if data['all']:
                try:
                    system_service.run_command(['hyperctl', 'stop', '$(hyperd list pod)'])
                    system_service.run_command(['hyperctl', 'stop', '$(hyperd list container)'])
                    system_service.run_command(['hyperctl', 'rm', '$(hyperd list pod)'])
                    system_service.run_command(['hyperctl', 'rm', '$(hyperd list container)'])
                    return {'success': True, 'body': 'success'}
                except Exception as e:
                    logger.info(e)
                    return {'success': False, 'body': e}

            for pod in data['pods']:
                try:
                    system_service.run_command(['hyperctl', 'stop', pod['id']])
                    system_service.run_command(['hyperctl', 'rm', pod['id']])
                except Exception as e:
                    logger.info(e)
                    return {'success': False, 'body': e}
            return {'success': True, 'body': 'success'}
    return {'success': False, 'body': 'No pods to remove'}
