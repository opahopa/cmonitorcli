import logging


logger = logging.getLogger(__name__)


def parse_status_stdout(result):
    stdout_lines = result.stdout.strip().split('\n')

    active = False
    run_time = None
    last_log = None
    warning = None
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
        if 'Warning' in result.stderr:
            warning = result.stderr.split("Warning", 1)[1].strip()

    return active, run_time, last_log, warning
