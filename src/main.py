import urllib2
import time
import datetime
import logging

#http://docutils.sourceforge.net/docs/index.html
"""Train a model to classify Foos and Bars.

Usage::

    >>> import klassify
    >>> data = [("green", "foo"), ("orange", "bar")]
    >>> classifier = klassify.train(data)

:param train_data: A list of tuples of the form ``(color, label)``.
:rtype: A :class:`Classifier <Classifier>`
"""
class zWayConnector():

    def __init__(self, host_name_and_port):
        self.host_name = host_name_and_port

    # Tools: converts to timestamp
    #------------------------------------------------
    def date_string_from_timestamp(self, time_stamp):
        try:
            return datetime.datetime.fromtimestamp(int(time_stamp))
        except:
            return time_stamp

    # Z-Way specific URL call / stupid
    #
    #------------------------------------
    def _zwaycall(self, device_id, url, instance_id = '0'):
        finalurl = self.host_name+'ZWaveAPI/Run/devices['+str(device_id)+'].instances['+str(instance_id)+'].' +url
        logging.debug(finalurl)
        response = urllib2.urlopen(finalurl)
        return response.read()

    # Z-Way compex URL call / advanced
    # return structure of values.
    #------------------------------------
    def _zwaycall_switch_multilevel(self, device_id, class_name, instance_id ='0'):
        level = self._zwaycall(device_id, class_name+'.data.level.value', instance_id)
        uptime = self.date_string_from_timestamp(self._zwaycall(device_id, class_name+'.data.level.updateTime', instance_id))
        seconds_old = (datetime.datetime.now() - uptime).seconds

        return [level, uptime, seconds_old]
    
    # Return actual state about the Thing
    #-------------------------------------
    def get_basic_level(self, device_id, instance_id ='0'):
        value = ['',0,0]
        value[0] = self._zwaycall(device_id,'Basic.data.level.value', instance_id) # value
        value[1] = self.date_string_from_timestamp(self._zwaycall(device_id, 'Basic.data.level.updateTime', instance_id)) # uptime
        value[2] = (datetime.datetime.now() - value[1]).seconds


        return value

        # Return actual state about the Thing
        # -------------------------------------

    def get_switch_binary_level(self, device_id, instance_id='0'):
        value = ['', 0, 0]
        value[0] = self._zwaycall(device_id, 'SwitchBinary.data.level.value', instance_id)  # value
        value[1] = self.date_string_from_timestamp(
            self._zwaycall(device_id, 'SwitchBinary.data.level.updateTime', instance_id))  # uptime
        value[2] = (datetime.datetime.now() - value[1]).seconds

        return value

    def basic_refresh(self, device_id, instance_id = '0'):
        return  self._zwaycall(device_id, 'Basic.Get()', instance_id)

    def switch_binary_refresh(self, device_id, instance_id = '0'):
        return  self._zwaycall(device_id, 'SwitchBinary.Get()', instance_id)

    def switch_on(self, device_id, instance_id = '0'):
        print "Switching ON..."
        value = self._zwaycall(device_id, 'SwitchBinary.Set(255)', instance_id)
        return value

    def switch_off(self, device_id, instance_id = '0'):
        print "Switching OFF..."
        value = self._zwaycall(device_id, 'SwitchBinary.Set(0)', instance_id)
        return value

    def turn_on(self, device_id, instance_id = '0'):
        print "Turning ON..."
        value = self._zwaycall(device_id, 'Basic.Set(255)', instance_id)
        return value

    def turn_off(self, device_id, instance_id = '0'):
        print "Turning OFF..."
        value = self._zwaycall(device_id, 'Basic.Set(0)', instance_id)
        return value

    def get_switch_level(self, device_id, instance_id=0):
        # read last value
        #value = self._zwaycall(device_id, 'SwitchMultilevel.data.level.value')
        res = self._zwaycall_switch_multilevel(device_id, "SwitchMultilevel",instance_id)
        return res

    
    def get_switch_level_and_refresh(self, device_id, instance_id=0):
        # read last value
        #value = self._zwaycall(device_id, 'SwitchMultilevel.data.level.value')
        res = self._zwaycall_switch_multilevel(device_id, "SwitchMultilevel",instance_id)

        # triger to refresh values
        self.switchLevelRefresh(device_id,instance_id)

        return res

    def switchLevelRefresh(self, device_id, instance_id):
        value = self._zwaycall(device_id, 'SwitchMultilevel.Get()',instance_id)
        return str(value)

class Kotol():
    device_id = '0'
    instance_id = '0'
    heating = '0'
    updated = 0
    seconds_old = 0


    def __init__(self, zway_conn, device_id, instance_id='0'):
        self.zway = zway_conn
        self.device_id = device_id
        self.instance_id = instance_id

    def turn_on(self):
        # Radiator heater actuar / actual status
        if self.heating=='false':
            print "Turning ON kotol..."
            self.zway.switch_on(self.device_id,self.instance_id)
            time.sleep(3)
            self.load_status()
        else:
            print "Kotol is turned ON already, do nothing."

    def turn_off(self):
        # Radiator heater actuar / actual status
        if self.heating=='true':
            print "Turning OFF kotol..."
            self.zway.switch_off(self.device_id, self.instance_id)
            time.sleep(3)
            self.load_status()
        else:
            print "Kotol is turned OFF already, do nothing."


    def load_status(self, refresh_timeout=60):
        # Radiator heater actuar / actual status
        actuator_data = self.zway.get_switch_binary_level(self.device_id,self.instance_id)
        self.heating = actuator_data[0]
        self.updated = actuator_data[1]
        self.seconds_old = actuator_data[2]

        #refresh if older that 5 minute
        if self.seconds_old>refresh_timeout:
            print "Data old {2} seconds. Kotol {0}.{1} force to refresh data.".format(self.device_id, self.instance_id, self.seconds_old)
            self.zway.basic_refresh(self.device_id,self.instance_id)

    def print_status(self):
        print "Kotol {0}.{1} Heating {2} [{3} seconds old data]".format(self.device_id,self.instance_id,self.heating, self.seconds_old)
        #time.sleep(60)

class Radiator():
    device_id = '0'
    instance_id = '0'
    valve = '0'
    updated = 0
    seconds_old = 0


    def __init__(self, zway_conn, device_id, instance_id='0'):
        self.zway = zway_conn
        self.device_id = device_id
        self.instance_id = instance_id

    def load_status(self, refresh_timeout=60):
        # Radiator heater actuar / actual status
        radiator_data = self.zway.get_switch_level(self.device_id,self.instance_id)
        self.valve = radiator_data[0]
        self.updated = radiator_data[1]
        self.seconds_old = radiator_data[2]

        #refresh if older that 5 minute
        if self.seconds_old>refresh_timeout:
            logging.debug("Radiator {0} force to refresh data.".format(self.device_id))
            self.zway.switchLevelRefresh(self.device_id,self.instance_id)

    def print_status(self):
        print "Radiator {0}.{1} Value {2} [{3} seconds old data]".format(self.device_id,self.instance_id,self.valve, self.seconds_old)
        #time.sleep(60)


class ThermalController():
    r_list = []
    a_list = []

    def __init__(self,zway_conn, radiator_list, actuator_list):
        self.a_list_names = actuator_list
        self.plug = zway_conn

        self.r_list = radiator_list
        self.a_list = actuator_list

        self._initialize_actuators_list(actuator_list)
        self._initialize_radiators_list(radiator_list)
        self.refresh_data(1)


    def parse_device_instance_from_string(self, device_string):
        device = ['','']
        if str(device_string).find('.')>0:
            device = str(device_string).split('.')
        else:
            device[0] = device_string
            device[1] = '0'

        return device

    def _initialize_radiators_list(self, r_list_names):
        # Radiator heater actuar / actual status
        i=0
        for radiator_name in r_list_names[:]:
            device = self.parse_device_instance_from_string(radiator_name)

            # Create list of Radiator objects and refresh data
            radiator = Radiator(self.plug, device[0], device[1])
            self.r_list[i] = radiator
            i+=1

    def _initialize_actuators_list(self, a_list_names):
        # Radiator heater actuar / actual status
        i=0
        for actuator_name in a_list_names[:]:
            device = self.parse_device_instance_from_string(actuator_name)

            # Create list of Radiator objects and refresh data
            kotol = Kotol(self.plug, device[0], device[1])
            self.a_list[i] = kotol
            i+=1

    def refresh_data(self, old_data_timeout):
        print "Read and refreshing values for Radiators..."
        for radiator in self.r_list[:]:
            radiator.load_status(old_data_timeout)
            radiator.print_status()

        print "Read and refreshing values for Actuators..."
        for device in self.a_list[:]:
            device.load_status(old_data_timeout)
            device.print_status()

    def kotol_turnon(self):
        for a in self.a_list[:]:
            a.turn_on()

    def kotol_turnoff(self):
        for a in self.a_list[:]:
            a.turn_off()

    def radiator_that_needs_heating(self, min_valve_openned = 20, ignore_older_that=50*5):
        nh = 0   #number of heating requests
        for r in self.r_list[:]:
            if (r.seconds_old<ignore_older_that) and (int(r.valve) > min_valve_openned):
                print "RadiatorID {0}.{1} valve={2} % openned, old={3} seconds".format(r.device_id, r.instance_id, r.valve, r.seconds_old)
                nh +=1

        print "{0} Number of Radiators need heat. /they have updated value before {2} seconds and valve > {1} openned/".format(nh, min_valve_openned, ignore_older_that)
        return nh

    def regulate(self, refresh_seconds = 50*5, min_valve_openned = 20, ignore_older_that=50*5):
        for i in range(500):
            print("Regulating...")
            self.refresh_data(ignore_older_that)
            nh = self.radiator_that_needs_heating(min_valve_openned, ignore_older_that)

            if nh>0:
                self.kotol_turnon()
            else:
                print "Turning OFF kotol..."
                self.kotol_turnoff()

            time.sleep(refresh_seconds)


#
#
#
#Z-way:
#Your user id: 102870
#Your kernel: gadeoBoofee2

logging.basicConfig(filename='ThermalRegulator.log',level=logging.DEBUG)
zway = zWayConnector('http://192.168.1.6:8083/')
regulator = ThermalController(zway, [16, 25, 26], [24.1, 24.2])

regulator.regulate(10)



# Blue Pulg  / actual status
#print "Actial Status:" + plug.getBasicLevel(27)
#plug.turnOn(27)
#time.sleep(10)
#print "Actial Status:" + plug.getBasicLevel(27)
#plug.turnOff(27)
#time.sleep(10)


#print "Actuial Radiator Status:" + plug.get_basic_level(27)

#for i in range(1,10):
#    print "Actial switchLevel [16]:{0}, [25]:{1}, [26]:{2}".format(plug.get_switch_level_and_refresh(16), plug.get_switch_level_and_refresh(25), plug.get_switch_level_and_refresh(26))
#    time.sleep(60)