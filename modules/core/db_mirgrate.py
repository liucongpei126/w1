import sqlite3
import os
from modules import  cbpi
from db import get_db


def execute_file(db_name,data_path,curernt_version, data):
    if curernt_version >= data["version"]:
        cbpi.app.logger.info("SKIP DB FILE: %s" % data["file"])
        return
    try:
        with sqlite3.connect(db_name) as conn:
            with open('%s/%s' %(data_path,data["file"]), 'r') as f:
                d = f.read()
                sqlCommands = d.split(";")
                cur = conn.cursor()
                for s in sqlCommands:
                    cur.execute(s)
                cur.execute("INSERT INTO schema_info (version,filename) values (?,?)", (data["version"], data["file"]))
                conn.commit()

    except sqlite3.OperationalError as err:
        print "EXCEPT"
        print err



@cbpi.initalizer(order=-9999)
def init(app=None):

    with cbpi.app.app_context():
        conn = get_db()
        cur = conn.cursor()
        current_version = None
        try:
            cur.execute("SELECT max(version) as m FROM schema_info")
            m = cur.fetchone()
            current_version =  m["m"]
        except:
            pass
        result = []
        for filename in os.listdir("./update"):
            if filename.endswith(".sql"):
                d = {"version": int(filename[:filename.index('_')]), "file": filename}
                result.append(d)
                execute_file("craftbeerpi.db","./update",current_version, d)


        conn = sqlite3.connect("sensor_log.db")
        cur = conn.cursor()
        current_version = []
        try:
            cur.execute("SELECT max(version) as m FROM schema_info")
            m = cur.fetchone()
            current_version = m["m"]
        except:
            pass
        result2 = []
        for filename in os.listdir("./update_log"):
            if filename.endswith(".sql"):
                d = {"version": int(filename[:filename.index('_')]), "file": filename}
                result2.append(d)
                execute_file("sensor_log.db", "./update_log", current_version, d)

'''
    with sqlite3.connect("sensor_log.db") as conn:
        cur = conn.cursor()
        current_version = None
        try:
            cur.execute("SELECT max(version) as m FROM schema_info")
            m = cur.fetchone()
            current_version = m["m"]
        except:
            pass

        result = []
        for filename in os.listdir("./update_log"):
            if filename.endswith(".sql"):
                d = {"version": int(filename[:filename.index('_')]), "file": filename}
                result.append(d)
                execute_file("sensor_log.db","./update_log",current_version, d)
'''

'''
def execute_file(curernt_version, data):
    if curernt_version >= data["version"]:
        cbpi.app.logger.info("SKIP DB FILE: %s" % data["file"])
        return
    try:
        with sqlite3.connect("craftbeerpi.db") as conn:
            with open('./update/%s' % data["file"], 'r') as f:
                d = f.read()
                sqlCommands = d.split(";")
                cur = conn.cursor()
                for s in sqlCommands:
                    cur.execute(s)
                cur.execute("INSERT INTO schema_info (version,filename) values (?,?)", (data["version"], data["file"]))
                conn.commit()

    except sqlite3.OperationalError as err:
        print "EXCEPT"
        print err

@cbpi.initalizer(order=-9999)
def init(app=None):

    with cbpi.app.app_context():
        conn = get_db()
        cur = conn.cursor()
        current_version = None
        try:
            cur.execute("SELECT max(version) as m FROM schema_info")
            m = cur.fetchone()
            current_version =  m["m"]
        except:
            pass
        result = []
        for filename in os.listdir("./update"):
            if filename.endswith(".sql"):
                d = {"version": int(filename[:filename.index('_')]), "file": filename}
                result.append(d)
                execute_file(current_version, d)


'''



