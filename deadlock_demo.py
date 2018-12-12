from multiprocessing import Process
from time import sleep

import records

SQL1 = """
begin;
set deadlock_timeout to 60;
UPDATE lockdemo set bar = :arg
           WHERE id = 1
       RETURNING bar;
"""

SQL2 = """
begin;
set deadlock_timeout to 60;
UPDATE lockdemo set bar = :arg
           WHERE id = 2
       RETURNING bar;
"""


def xact_1():
    db = records.Database()
    db.query(SQL1, arg='hey')
    sleep(5)
    db.query(SQL2, arg='hey')


def xact_2():
    db = records.Database()
    db.query(SQL2, arg='yo')
    sleep(5)
    db.query(SQL1, arg='you')


if __name__ == "__main__":
    y = Process(target=xact_1)
    z = Process(target=xact_2)
    z.start()
    y.start()
