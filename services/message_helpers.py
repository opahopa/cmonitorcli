import logging, traceback
import json

from models.report import ReportService
from models.message import Message, MessageCommands, MessageStatus
from services.utils import get_fee
from version import CLI_VERSION

logger = logging.getLogger(__name__)


def parse_message(content):
    try:
        content = json.loads(content)
        msg = Message(type=content["type"], command=content["command"])
        try:
            msg.status = content["status"]
        except KeyError:
            pass
        try:
            msg.body = content["body"]
        except KeyError:
            pass
        try:
            msg.hostname = content["hostname"]
        except KeyError:
            pass
        return msg
    except Exception as e:
        # logger.error(e)
        traceback.print_exc(e)


def result_to_json_response(type, status, hostname, report_system=None, report_codius=None, body=None,
                            report_extra_services=None):
    result = {}
    result['type'] = "REPORT"
    result['command'] = type.name
    result['status'] = status.name
    result['hostname'] = hostname
    result['cli_version'] = CLI_VERSION

    if body:
        result['body'] = body

    if report_system and report_codius:
        result['body'] = {
            'system': report_system,
            'codius': report_codius
        }

    if report_extra_services:
        result['body']['extra_services'] = report_extra_services

    if status is MessageStatus.ERROR:
        return json.dumps(result)

    if type is MessageCommands.STATUS_ALL or type is MessageCommands.STATUS_CLI_UPDATE:
        for i in range(0, len(report_system)):
            if isinstance(report_system[i], ReportService):
                report_system[i] = report_system[i].toDict()

        for i in range(0, len(report_extra_services)):
            if isinstance(report_extra_services[i], ReportService):
                report_extra_services[i] = report_extra_services[i].toDict()

        result['body']['system'] = report_system
        result['body']['codius'] = report_codius
        result['body']['extra_services'] = report_extra_services

    #     for k, v in content.items():
    #         try:
    #             if isinstance(content[k], ReportService):
    #                 content[k] = v.toDict()
    #         except Exception as e:
    #             logger.error(e)

    return json.dumps(result, default=str)


""""""""""""""""""""""""""""""""""""""""
:returns
decimal dialy_income with precision 5.

and

:int: pods_count 
"""""""""""""""""""""""""""""""""""""""""

def calc_income(pods_log):
    # timer_start = timer()

    pods_activity, pods_count = podsActivity(pods_log)
    try:
        fee = get_fee()
    except KeyError as e:
        pass

    income_24 = 0

    for k, v in pods_activity.items():
        if v['fee'] is not 0:
            income_24 += v['duration'] * fee_per_sec(v['fee'])
        else:
            try:
                income_24 += v['duration'] * fee_per_sec(fee)
            except KeyError as e:
                return None

    # timer_end = timer()
    # print(timer_end - timer_start)

    return round(income_24, 5), pods_count


def fee_per_sec(fee):
    return fee / 30 / 24 / 60 / 60


""""""""""""""""""""""""""""""""""""""""
Data writen to db every 3 sec, so reasonable diff is 60 sec
(bot reconnects, etc)

Returns dict:pods_activity 
pods_activity[id]: pod id
pods_activity[id]['duration']: total pod execution time (seconds)
pods_activity[id]['timestamps']: tuple(timestamp, fee)
pods_activity[id]['fee']: associated average fee

and 'int' pods_count

"""""""""""""""""""""""""""""""""""""""""


def podsActivity(pods_log):
    try:
        pod_ids = []
        for log in pods_log:
            time, pods = log[0], log[1]
            if pods is not None and len(pods) > 0:
                pod_ids.extend([pod['id'] for pod in json.loads(pods)])

        pod_ids_unique = list(set(pod_ids))

        pods_activity = {}
        # associate timestamps with pod id's
        # pods_activity[id]['timestamps'] contains tuples '(timestamp, fee)'
        for id in pod_ids_unique:
            pods_activity[id] = {}
            pods_activity[id]['timestamps'] = []

            for log in pods_log:
                time, pods, fee = log[0], log[1], log[2]
                if pods is not None and len(pods) > 0:
                    if id in [pod['id'] for pod in json.loads(pods)]:
                        pods_activity[id]['timestamps'].append((time, fee))

            pods_activity[id]['timestamps'].sort(key=lambda tup: tup[0])

        # print(pprint.pprint(pods_activity))

        # calculate total run duration for each pod
        for k, v in pods_activity.items():
            pods_activity[k]['duration'] = 0
            pods_activity[k]['fee'] = 0

            max_interruption = 60
            starts = [t[0] for t in v['timestamps']][:-1]
            ends = [t[0] for t in v['timestamps']][1:]
            durations = zip(starts, ends)
            for start, end in durations:
                delta = (end - start).total_seconds()
                if delta < max_interruption:
                    pods_activity[k]['duration'] += delta

            pods_activity[k]['fee'] = sum([t[1] for t in v['timestamps']]) / len(v['timestamps'])

            # print(f"added: {pods_activity[k]['duration']}")
            # diff = v['timestamps'][-1] - v['timestamps'][0]
            # print(f"real: {diff.seconds}")

        return pods_activity, len(pod_ids_unique)
    except:
        traceback.print_exc()

    pass
