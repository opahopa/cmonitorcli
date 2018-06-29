import sqlite3, traceback
import datetime
import json


class DbService(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self):
        try:
            self.conn = sqlite3.connect('cmonitorcli.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.c = self.conn.cursor()

            self.c.execute('''CREATE TABLE IF NOT EXISTS system_info
                         (hostname text not null, status_hyperd boolean, status_moneyd boolean, status_codiusd boolean
                         pods text[])''')
            self.c.execute('''CREATE TABLE IF NOT EXISTS codius_history
                         (record_time timestamp, pods json[])''')
        except BaseException as error:
            print('An exception occurred on connecting to sqllite: {}'.format(error))

    def write_hostname(self, hostname):
        try:
            self.c.execute("INSERT INTO system_info (hostname) VALUES ('" + hostname + "')")
            self.conn.commit()
        except BaseException as error:
            print('An exception occurred on writing hostname to sqllite: {}'.format(error))

    def get_pods_in24hours(self):
        self.c.execute("SELECT record_time as [timestamp], pods FROM codius_history WHERE record_time >= datetime('now','-1 day')")
        res = self.c.fetchall()
        if res[0] is not None:
            return res
        else:
            return []

    """""
    pods:
    [{
        'id': ss[0],
        'name': ss[1],
        'vm_name': ss[2],
        'status': ss[3]
    }]
    """""
    def write_pods_status(self, pods):
        try:
            time = datetime.datetime.now()
            self.c.execute("INSERT INTO codius_history (record_time, pods) VALUES (?, ?)", (time, json.dumps(pods),))
            self.conn.commit()
        except BaseException as error:
            print('An exception occurred on writing pods history to sqllite: {}'.format(error))
            traceback.print_exc()

    def get_hostname(self):
        self.c.execute("SELECT hostname FROM system_info")
        res = self.c.fetchone()
        if res[0] is not None:
            return res[0]
        else:
            return None
