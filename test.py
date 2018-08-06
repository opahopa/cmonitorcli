import itertools, datetime, traceback, json

from services.db_service import DbService

def calc_income(pods_log):
    # timer_start = timer()
    pods_activity, pods_count = podsActivity(pods_log)
    try:
        fee = 5
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

def stats_all():
    pods_30 = [
        (datetime.datetime(2018, 7, 1, 22, 33, 39, 86170), json.dumps([
            {
                'id': 'foihew3434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 1, 22, 33, 42, 33213), json.dumps([
            {
                'id': 'foihew3434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 1, 22, 33, 44, 898234), json.dumps([
            {
                'id': 'foihew3434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 2, 22, 33, 47, 893731), json.dumps([
            {
                'id': 'foihew3434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 2, 22, 33, 50, 928946), json.dumps([
            {
                'id': 'foihew3434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 3, 22, 33, 53, 895617), json.dumps([
            {
                'id': 'foihew34ff34h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            },
            {
                'id': 'foihergergf34h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 5, 22, 35, 7, 116182), json.dumps([
            {
                'id': 'foihew3sd434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 5, 22, 35, 10, 105035), json.dumps([
            {
                'id': 'foihew343dsf4h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            },
            {
                'id': 'foihrhtrhtf34h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6),
        (datetime.datetime(2018, 7, 15, 22, 35, 13, 193428), json.dumps([
            {
                'id': 'foihew3434h235',
                'name': 'foihewoheowfh235',
                'vm_name': 'foihewoheowfh235',
                'status': 'activate'
            }
        ]), 6)
    ]

    dialy = []
    for dt, grp in itertools.groupby(pods_30, key=lambda x: x[0].date()):
        tmp = []
        for v in list(grp):
            tmp.append(v)


        income, count = calc_income(tmp)
        dialy.append({'date': dt, 'income': income, 'count': count})

    for d in dialy:
        print(d)


if __name__ == "__main__":
    stats_all()