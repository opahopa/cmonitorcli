import sqlite3


class DbService(object):
    def __init__(self):
        try:
            self.conn = sqlite3.connect('cmonitorcli.db')
            self.c = self.conn.cursor()

            self.c.execute('''CREATE TABLE IF NOT EXISTS info
                         (hostname text not null, status_hyperd boolean, status_moneyd boolean, status_codiusd boolean
                         pods text[])''')
        except BaseException as error:
            print('An exception occurred on connecting to sqllite: {}'.format(error))

    def write_hostname(self, hostname):
        try:
            self.c.execute("INSERT INTO info (hostname) VALUES ('"+hostname+"')")
            self.conn.commit()
        except BaseException as error:
            print('An exception occurred on writing hostname to sqllite: {}'.format(error))

    def get_hostname(self):
        self.c.execute("SELECT hostname FROM info")
        res = self.c.fetchone()
        if res[0] is not None:
            return res[0]
        else:
            return None
