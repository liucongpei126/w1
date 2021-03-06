import sqlite3

from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property


@cbpi.controller
class Hysteresis(KettleController):

    # Custom Properties

    on = Property.Number("Offset On", True, 0, description="Offset below target temp when heater should switched on. Should be bigger then Offset Off")
    off = Property.Number("Offset Off", True, 0, description="Offset below target temp when heater should switched off. Should be smaller then Offset Off")

    def stop(self):
        '''
        Invoked when the automatic is stopped.
        Normally you switch off the actors and clean up everything
        :return: None
        '''
        super(KettleController, self).stop()
        self.heater_off()



    def run(self):
        '''
        Each controller is exectuted in its own thread. The run method is the entry point
        :return:
        '''

        count =0
        status = 0
        pre_status = 0
        while self.is_running():

            if self.get_temp() < self.get_target_temp() - float(self.on):
                self.heater_on(100)
                status = 1
            elif self.get_temp() >= self.get_target_temp() - float(self.off):
                self.heater_off()
                status = 0

            if 0==count%15 or pre_status != status :
                try:
                    with sqlite3.connect("lcp_log.db") as conn:
                        c = conn.cursor()
                        pre_status = status
                        sql = "insert into tbksensor_log(nTime,nKettleID,nStatus,nCur_Tem,nTarget_Tem) values(datetime('now','localtime'),%d,%d,%.2f,%.2f)"%(self.kettle_id,status,self.get_temp(),self.get_target_temp())
                        #print sql
                        c.execute(sql)

                        if 0==count%(15*128):
                            sql = "delete from tbksensor_log where nTime < datetime('now','localtime','start of day','-8 day');"
                            c.execute(sql)
                        conn.commit()
                        conn.close()

                except :
                    pass

            self.sleep(1)
            count = count + 1