
//  https://technology.amis.nl/2016/01/14/simple-security-system-using-raspberry-pi-2b-razberry-fibaro-motion-sensor-fgms-001/
//  Create within z-way Javasript application
//  Copy this files to /opt/z-way-server/automation/ThermalRegulator/src/
//  Modify file .syscommands and add there command "/usr/bin/python /opt/z-way-server/automation/ThermalRegulator/src/main.py"

//In the JavaScript code I could now call these scripts like:
//system(‘/usr/bin/python /opt/z-way-server/automation/ThermalRegulator/src/trigger.py’, value);
//
this.bindFunc1 = function (zwayName) {
  if (zwayName != "zway")
   return; // you want to bind to default zway instance

  var devices = global.ZWave[zwayName].zway.devices;

 //bind function on_change value
 zway.devices[3].instances[0].commandClasses[48].data[1].level.bind(function() {
  if (this.value == true)
    debugPrint("Executing trigger");
    system('/usr/bin/python /opt/z-way-server/automation/ThermalRegulator/src/trigger.py');
});

 zway.devices[3].instances[0].commandClasses[49].data[1].val.bind(function() {
  debugPrint("Saving measure");
  system('/usr/bin/python /opt/z-way-server/automation/ThermalRegulator/src/savemeasure.py','Temperature',this.value);
});

 zway.devices[3].instances[0].commandClasses[49].data[3].val.bind(function() {
  debugPrint("Saving measure");
  system('/usr/bin/python /opt/z-way-server/automation/ThermalRegulator/src/savemeasure.py','Luminescence',this.value);
});

 zway.devices[3].instances[0].Battery.data.last.bind(function() {
  debugPrint("Saving measure");
  system('/usr/bin/python /opt/z-way-server/automation/ThermalRegulator/src/savemeasure.py','Battery',this.value);
});

};
// process all active bindings
if (global.ZWave) {
  global.ZWave().forEach(this.bindFunc1);
}

// and listen for future ones
global.controller.on("ZWave.register", this.bindFunc1);