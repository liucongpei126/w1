#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time,os,sys
import json
import sqlite3
import requests 
import socket
import ConfigParser
import RPi.GPIO as GPIO

def Alert(msg):
    url = "https://oapi.dingtalk.com/robot/send?access_token=d30df6a04ddba9309e15440e9877be38fe991b0ab835ed6c736f1e36980b3cc8"
    headers = {"Content-Type": "application/json"}
    data = {"msgtype": "text", "text": {"content": msg}}
    try:
        r = requests.post(
            url,
            data=json.dumps(data), headers=headers)
    except:
        pass

def DingDingNotice(last_change_tick,cur_io_status):
    last_ltime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_change_tick))
    cur_ltime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
    host_name = socket.gethostname()
    status = ""
    if False==cur_io_status:
        status = "启动"
    else:
        status = "关闭"
    msg = "树莓派 {name}\n事件: {flag1}\n当前状态: {status}\n上次执行时间: {time1}\n当前时间: {time2}\n".format(name=host_name,flag1="真空泵",status=status,time1=last_ltime,time2=cur_ltime)
    Alert(msg)


class MyIoAct():
    def __init__(self):
        self.pre_io_status = True
        self.cur_io_status = True
        self.cur_ioid = 0
        self.do_pump_monitor = True
        self.pump_start_ttl = 120
        self.pump_stop_ttl = 300

    def set_io_id(self,ioid):
        self.cur_ioid = ioid

    def update_monitor_conf(self):
        cp = ConfigParser.ConfigParser(allow_no_value=True)
        try:
            cp.read("/home/pi/myconfig/pump.ini")
            try:
                self.do_pump_monitor = cp.getboolean("pump", "Monitor")
            except:
                self.do_pump_monitor = True
            try:
                self.pump_start_ttl = cp.getint("pump","StartTimeout")
            except:
                self.pump_start_ttl = 120
            try:
                self.pump_stop_ttl = cp.getint("pump","StopTimeout")
            except:
                self.pump_stop_ttl = 300
        except:
            self.do_pump_monitor = True
            self.pump_stop_ttl = 300
            self.pump_start_ttl = 120

    def  run(self):
        time.sleep(15)
        count = 0
    	GPIO.setmode(GPIO.BCM)
    	GPIO.setup(self.cur_ioid,GPIO.IN)
        new_start_flag = 0
        last_change_tick = int(time.time())
        self.update_monitor_conf()
        while True:
            count = count + 1

            time.sleep(1)
            if 0==count % 10 :
                self.update_monitor_conf()
            #print "run............................%d"%(count)
            self.cur_io_status = GPIO.input(self.cur_ioid)
            cur_tick = int(time.time())
            if new_start_flag and True == self.do_pump_monitor:
                if self.cur_io_status == True:
                    if cur_tick - last_change_tick > self.pump_stop_ttl:
                        new_start_flag = 0
                        DingDingNotice(last_change_tick, self.cur_io_status)
                else :
                    if cur_tick - last_change_tick > self.pump_start_ttl:
                        new_start_flag = 0
                        DingDingNotice(last_change_tick, self.cur_io_status)

            # if cur_tick - last_change_tick > 240 and new_start_flag  :
            #     new_start_flag = 0
            #     DingDingNotice(last_change_tick,self.cur_io_status)

            if 0==count% 300 or self.pre_io_status != self.cur_io_status:
                if self.pre_io_status != self.cur_io_status:
                    last_change_tick = cur_tick
                    if 0==new_start_flag:
                        new_start_flag = 1
                try:
                    with sqlite3.connect("lcp_log.db") as conn:
                        c = conn.cursor()
                        self.pre_io_status = self.cur_io_status
                        sql = "insert into tbmygpio_log(nTime,nIO,nStatus) values(datetime('now','localtime'),%d,%d)"%(self.cur_ioid,self.cur_io_status)
                        #print sql
                        c.execute(sql)

                        if 0==count%(15*128):
                            sql = "delete from tbmygpio_log where nTime < datetime('now','localtime','start of day','-8 day');"
                            c.execute(sql)
                        conn.commit()
                        conn.close()

                except :
                    #print "open sqlite db error...."
                    pass


def my_io_act_start(ioid):
    obj = MyIoAct()
    obj.set_io_id(ioid)
    obj.run()
