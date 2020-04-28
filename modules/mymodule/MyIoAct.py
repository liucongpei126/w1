#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time,os,sys
import json
import sqlite3

import RPi.GPIO as GPIO


class MyIoAct():
    def __init__(self):
        self.pre_io_status = True
        self.cur_io_status = True
        self.cur_ioid = 0

    def set_io_id(self,ioid):
        self.cur_ioid = ioid

    def  run(self):
        time.sleep(15)
        count = 0
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(self.cur_ioid,GPIO.IN)
        while True:
            count = count + 1

            time.sleep(1)
            #print "run............................%d"%(count)
            self.cur_io_status = GPIO.input(self.cur_ioid)
            if 0==count% 15 or self.pre_io_status != self.cur_io_status:
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
