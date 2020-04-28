#!/usr/bin/env python

from modules import socketio, app, cbpi
from modules.mymodule import MyIoAct as IoAct
import thread

try:
  port = int(cbpi.get_config_parameter('port', '5000'))
except ValueError:
  port = 5000



def test_thread(ioid):
    print "start..... test thread .....%d"%(ioid)
    obj = IoAct.MyIoAct()
    obj.set_io_id(ioid)
    obj.run()

try:
  print "start my io thread......1"
  #thread.start_new_thread(my_io_act_atart,(40,))
  thread.start_new_thread(test_thread,(21,))
  print "start my io thread......2"
except:
  print "Error: unable to start thread my_io_act_start"


socketio.run(app, host='0.0.0.0', port=port)

