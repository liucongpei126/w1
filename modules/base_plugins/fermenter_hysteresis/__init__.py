from modules import cbpi
from modules.core.controller import KettleController, FermenterController
from modules.core.props import Property
import sqlite3


@cbpi.fermentation_controller
class Hysteresis(FermenterController):

    heater_offset_min = Property.Number("Heater Offset ON", True, 0, description="Offset as decimal number when the heater is switched on. Should be greater then 'Heater Offset OFF'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature")
    heater_offset_max = Property.Number("Heater Offset OFF", True, 0, description="Offset as decimal number when the heater is switched off. Should be smaller then 'Heater Offset ON'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature")
    cooler_offset_min = Property.Number("Cooler Offset ON", True, 0, description="Offset as decimal number when the cooler is switched on. Should be greater then 'Cooler Offset OFF'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees above the target temperature")
    cooler_offset_max = Property.Number("Cooler Offset OFF", True, 0, description="Offset as decimal number when the cooler is switched off. Should be less then 'Cooler Offset ON'. For example a value of 1 switches off the cooler if the current temperature is 1 degree above the target temperature")

    def stop(self):
        super(FermenterController, self).stop()

        self.heater_off()
        self.cooler_off()

    def run(self):
        count = 0
        status = 0
        pre_status = 0
        #print "running......"
        while self.is_running():
            count = count + 1
            #print "running...... " + self.__class__.__name__
            target_temp = self.get_target_temp()
            start_temp = self.get_start_temp()
            stop_temp = self.get_stop_temp()
            temp = self.get_temp()
            temp2 = self.get_temp2()

            #print "temp2..... " + str(temp2)
            flag = 0
            if start_temp is not None and temp2 is not None:
                if start_temp >= temp2:
                    flag = 1
            else :
                flag = 1

            if flag == 1 and temp + float(self.heater_offset_min) <= target_temp:
                self.heater_on(100)
                status = 1
            elif temp + float(self.heater_offset_max) >= target_temp:
                self.heater_off()
                status = 0
            elif stop_temp is not None and temp2 is not None and stop_temp <= temp2:
                self.heater_off()
                status = 0


            if temp >= target_temp + float(self.cooler_offset_min):
                self.cooler_on(100)
            elif temp <= target_temp + float(self.cooler_offset_max):
                self.cooler_off()

            if 0==count%1800 or pre_status != status :
                try:
                    with sqlite3.connect("lcp_log.db") as conn:
                        c = conn.cursor()
                        pre_status = status
                        sql = "insert into tbfsensor_log(nTime,nFermenterID,nStatus,nCur_Tem,nTarget_Tem) values(datetime('now','localtime'),%d,%d,%.2f,%.2f)"%(self.fermenter_id,status,self.get_temp(),self.get_target_temp())
                        #print sql
                        c.execute(sql)

                        if 0==count%(15*128):
                            sql = "delete from tbfsensor_log where nTime < datetime('now','localtime','start of day','-3 day');"
                            c.execute(sql)
                        conn.commit()
                        conn.close()

                except :
                    pass

            self.sleep(1)
