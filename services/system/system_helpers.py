import logging

logger = logging.getLogger(__name__)


def parse_service_report_stdout(result):
    stdout_lines = result.stdout.strip().split('\n')
    active = False
    run_time = None
    last_log = None
    warning = None
    error = None
    installed = True
    txt_start = 0
    try:
        for i in range(0, len(stdout_lines)):
            if 'Active:' in stdout_lines[i] and 'running' in stdout_lines[i]:
                active = True
                run_time = stdout_lines[i].split('since', 1)[1].strip()
            if not stdout_lines[i]:
                txt_start = i

        if txt_start != 0:
            last_log = "\n".join(stdout_lines[txt_start:len(stdout_lines)])
            last_log = last_log[1:len(last_log)]
    except Exception as e:
        logger.error(e)
        pass

    if len(result.stderr) > 5:
        error = result.stderr
        if 'Warning' in result.stderr:
            warning = result.stderr.split("Warning", 1)[1].strip()
        if 'could not be found' in result.stderr:
            installed = False

    return active, run_time, last_log, warning, error, installed


def parse_hyperctl_list(result):
    lines = result.stdout.strip().split('\n')
    active_pods = []

    for i in range(0, len(lines)):
        if 'POD ID' not in lines[i] and 'POD Name' not in lines[i]:
            ss = lines[i].split()
            active_pods.append({
                'id': ss[0],
                'name': ss[1],
                'vm_name': ss[2],
                'status': ss[3]
            })

    return active_pods


def parse_memory_usage(result):
    lines = result.stdout.strip().split('\n')
    memory = {}

    for i in range(0, len(lines)):
        if 'Mem:' in lines[i]:
            ss = lines[i].split()
            memory = {
                'total': int(ss[1]),
                'used': int(ss[2])
            }

    return memory

def parse_fee(result):
    return int(result.stdout.strip())