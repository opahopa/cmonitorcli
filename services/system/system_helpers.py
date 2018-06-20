def parse_status_stdout(stdoutstr):
    stdout_lines = stdoutstr.stdout.strip().split('\n')

    active = False
    run_time = None
    last_log = None
    txt_start = 0
    for i in range(0, len(stdout_lines)):
        if 'Active:' in stdout_lines[i] and 'running' in stdout_lines[i]:
            active = True
            run_time = stdout_lines[i].split('since', 1)[1].strip()
        if not stdout_lines[i]:
            txt_start = i

    if txt_start != 0:
        last_log = "\n".join(stdout_lines[txt_start:len(stdout_lines)])
    return active, run_time, last_log[1:len(last_log)]
