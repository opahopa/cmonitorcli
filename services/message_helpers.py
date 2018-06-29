import logging, traceback
import sys
import json, pprint


from timeit import default_timer as timer
from models.report import ReportService
from services.db_service import DbService
from models.response import ResponseTypes, ResponseStatus
from models.message import MessageCommands, MessageStatus

sys.path.append("..")

from models.message import Message

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
        return msg
    except Exception as e:
        logger.error(e)
        # traceback.print_exc()


def result_to_json_response(report_system, report_codius, type, status, hostname):
    result = {}
    result['type'] = "REPORT"
    result['command'] = type.name
    result['status'] = status.name
    result['hostname'] = hostname
    result['body'] = {
        'system': report_system,
        'codius': report_codius
    }

    if status is MessageStatus.ERROR:
        return json.dumps(result)

    if type is MessageCommands.STATUS_ALL or type is MessageCommands.STATUS_CLI_UPDATE:
        for i in range(0, len(report_system)):
            if isinstance(report_system[i], ReportService):
                report_system[i] = report_system[i].toDict()

        result['body']['system'] = report_system
        result['body']['codius'] = report_codius

    #     for k, v in content.items():
    #         try:
    #             if isinstance(content[k], ReportService):
    #                 content[k] = v.toDict()
    #         except Exception as e:
    #             logger.error(e)

    return json.dumps(result)


def calcDialyIncome(pods_log):
    pods_activity = podsActivity(pods_log)
    total_duration = 0

    # print(pprint.pprint(pods_activity))

    for k, v in pods_activity.items():
        total_duration += v['duration']

    print(total_duration)


""""""""""""""""""""""""""""""""""""""""
Data writen to db every 3 sec, so reasonable diff is 60 sec
(bot reconnects, etc)

Returns dict:pods_activity 
pods_activity[id]: pod id
pods_activity[id]['duration']: total pod execution time (seconds)
pods_activity[id]['timestamps']: associated timestamps

"""""""""""""""""""""""""""""""""""""""""
def podsActivity(pods_log):
    try:
        timer_start = timer()

        pod_ids = []
        for log in pods_log:
            time, pods = log[0], log[1]
            if pods is not None and len(pods) > 0:
                pod_ids.extend([pod['id'] for pod in json.loads(pods)])

        pod_ids_unique = list(set(pod_ids))

        pods_activity = {}
        for id in pod_ids_unique:
            pods_activity[id] = {}
            pods_activity[id]['timestamps'] = []

            for log in pods_log:
                time, pods = log[0], log[1]
                if pods is not None and len(pods) > 0:
                    if id in [pod['id'] for pod in json.loads(pods)]:
                        pods_activity[id]['timestamps'].append(time)

            pods_activity[id]['timestamps'].sort()

        print(pprint.pprint(pods_activity))

        # calculate total run duration for each pod
        for k, v in pods_activity.items():
            pods_activity[k]['duration'] = 0

            start, next = v['timestamps'][0], ''
            for time in v['timestamps']:
                next = time
                diff = next - start

                if diff.seconds < 30:
                    pods_activity[k]['duration'] += diff.seconds
                else:
                    print("diff: %s" % diff.seconds)

                start = next

            print(f"added: {pods_activity[k]['duration']}")
            diff = v['timestamps'][-1] - v['timestamps'][0]
            print(f"real: {diff.seconds}")




        timer_end = timer()
        print(timer_end - timer_start)

        return pods_activity
    except:
        traceback.print_exc()

    pass
