from datetime import datetime
from multiprocessing import Process
from time import sleep

import records

SQL = """
UPDATE lockdemo set bar = :arg
           WHERE id = 2
       RETURNING bar;
"""


def xact_1():
    db = records.Database()
    start = datetime.utcnow().isoformat()
    for i in range(10):
        with db.transaction() as t:
            arg = '-'.join(['hey', str(i)])
            r = db.query(SQL, arg=arg)
            edt = datetime.utcnow().isoformat()
            print(start, dict(r.all()[0]), edt)
            t.commit()


def xact_2():
    db2 = records.Database()
    for i in range(10):
        with db2.transaction() as t2:
            db2.query('select * from lockdemo for update')
            sleep(i * 3)  # dummy processing
            t2.commit()
    edt = datetime.utcnow().isoformat()
    print(edt)


if __name__ == "__main__":
    y = Process(target=xact_1)
    z = Process(target=xact_2)
    z.start()
    y.start()
