import sqlite3, traceback
import datetime
import json
import logging

logger = logging.getLogger(__name__)

class DbService(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        pass

    def __init__(self):
        try:
            self.conn = sqlite3.connect('cmonitorcli.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.c = self.conn.cursor()

            self.c.execute('''CREATE TABLE IF NOT EXISTS system_info
                         (hostname text not null, status_hyperd boolean, status_moneyd boolean, status_codiusd boolean
                         pods text[])''')
            self.c.execute('''CREATE TABLE IF NOT EXISTS codius_history
                         (record_time timestamp, pods json[], fee integer, contracts_active integer)''')

            self.c.execute('PRAGMA user_version')
            v = int(self.c.fetchone()[0])
            if v < 1:
                self.c.execute('ALTER TABLE codius_history ADD COLUMN contracts_active integer')
                self.c.execute('PRAGMA user_version = 1')

        except BaseException as error:
            print('An exception occurred on connecting to sqllite: {}'.format(error))

    def write_hostname(self, hostname):
        try:
            self.c.execute("INSERT INTO system_info (hostname) VALUES ('" + hostname + "')")
            self.conn.commit()
        except BaseException as error:
            print('An exception occurred on writing hostname to sqllite: {}'.format(error))

    def get_codiusd_in_n_days(self, n):
        try:
            self.c.execute("SELECT record_time as [timestamp], pods, fee, contracts_active"
                           " FROM codius_history WHERE record_time >= datetime('now', '-{} day')".format(n))
            res = self.c.fetchall()
            if res[0] is not None:
                return res
            else:
                return []
        except IndexError:
            return []

    """""
    pods:
    [{
        'id': ss[0],
        'name': ss[1],
        'vm_name': ss[2],
        'status': ss[3],
        'fee': ''
    }]
    """""
    def write_pods_status(self, codius):
        # pods = [
        #     {
        #         'id': 'foihew3434h235',
        #         'name': 'foihewoheowfh235',
        #         'vm_name': 'foihewoheowfh235',
        #         'status': 'activate'
        #     },
        #     {
        #         'id': 'foih343434h235',
        #         'name': 'foihewoheowfh235',
        #         'vm_name': 'foihewoheowfh235',
        #         'status': 'activate'
        #     },
        #     {
        #         'id': 'foi343555heowfh235',
        #         'name': 'foihewoheowfh235',
        #         'vm_name': 'foihewoheowfh235',
        #         'status': 'activate'
        #     }
        # ]
        if codius['contracts_active']:
            contracts_active = int(codius['contracts_active'])
        else:
            contracts_active = 0

        try:
            time = datetime.datetime.now()
            self.c.execute("INSERT INTO codius_history (record_time, pods, fee, contracts_active) VALUES (?, ?, ?, ?)"
                           , (time, json.dumps(codius['pods']), int(codius['fee']), contracts_active,))
            self.conn.commit()
        except BaseException as error:
            logger.error('A BaseException occurred on writing pods history to sqllite: {}'.format(error))
        except TypeError as error:
            logger.error('An TypeError occurred on writing pods history to sqllite: {}'.format(error))
        except Exception as error:
            logger.error('An Exception occurred on writing pods history to sqllite: {}'.format(error))

    def get_hostname(self):
        self.c.execute("SELECT hostname FROM system_info")
        res = self.c.fetchone()
        if res[0] is not None:
            return res[0]
        else:
            return None
