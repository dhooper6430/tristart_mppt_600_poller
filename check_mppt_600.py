#!/usr/bin/env python

# Import modbus functions

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# Import standard functions & set some debugging parameters

import logging, os, sys
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)


# Function to read morningstar modbus, 16bit floating values & convert to float32

def f162f32(f16):
    f32 = float=(0)
    sign = (f16 & 0x8000) >> 15
    exponent = ((f16 & 0x7C00) >> 10)
    fraction = (f16 & 0x03ff) / 1024.0
    f32 = (fraction + 1.0) * pow(2.0,(exponent -15))
    return f32

# Connect to modbus client, IP address is specified on cmd line, tcp port 502

client = ModbusClient (host=sys.argv[1], port=502)

#  Define the State list

state = ['Start', 'Night Check', 'Disconnect', 'Night', 'Fault', 'MPPT', 'Absorption', 'Float', 'Equalize', 'Slave', 'Fixed']

#FIXME -  Read all holding registers from 0 to 50, probably thrashing the balls of this thing reading some registers .. needs to be put in an array to just read the individual reg's we are after

rr = client.read_holding_registers(0,72,unit=1)

# Specify our registers below and call the function to get the correct value

# Battery Voltage
battV = f162f32( rr.registers[38])

# Battery Charging Current
battcc = f162f32( rr.registers[39])

# Solar panel array voltage
arrayV = f162f32( rr.registers[27])

# Solar panel array current
arrayC = f162f32( rr.registers[29])

# Temperature Sensor - heatsink
tempH = f162f32( rr.registers[35])

# Current alarm if any
alarm = ( rr.registers[50])

# Temperature of batteries 
batt_temp = f162f32( rr.registers[37])

# Daily amp hours in collected
daily_amp_hours = f162f32( rr.registers[67])

## Print some stuff for debug purposes

print "Battery Sense Volts : %.4f" % battV +" Volts"
print "Battery Charging Current : %.4f" % battcc +" Amps"
print "Array Voltage : %.4f" % arrayV +" Volts"
print "Array Current : %.4f" % arrayC +" Amps"
print "Heatsink Temperature : %.2f" % tempH +" Degrees"
print "Battery Temperature : %.2f" % batt_temp +" Degrees"
print "State : %s" % state[alarm]
print "Daily Amp Hours In : %.4f" % daily_amp_hours +" Amps"


# Output our standard nagios stanza with perf data
# I alarm at 48v, modify to suit your own requirements, float voltage is normally around 56v 

if battV < 48.00:
    print "Battery Volts is WARNING - Volts:%.4f"%battV +" | battvolts=%.4f"%battV +" BatteryChargeCurrent=%.4f"%battcc +" ArrayVoltage=%.4f"%arrayV +" ArrayCurrent=%.4f"%arrayC +" HeatsinkTemperature=%.2f"%tempH +" BatteryTemperature=%.2f"%batt_temp +" DailyAmpHoursIn=%.4f"%daily_amp_hours
    sys.ext(1)

elif alarm == 4:
    print "Fault Detected"
    sys.exit(2)

else:
     print "Battery Volts is OK - Volts:%.4f"%battV +" | battvolts=%.4f"%battV +" BatteryChargeCurrent=%.4f"%battcc +" ArrayVoltage=%.4f"%arrayV +" ArrayCurrent=%.4f"%arrayC +" HeatsinkTemperature=%.2f"%tempH +" BatteryTemperature=%.2f"%batt_temp +" DailyAmpHoursIn=%.4f"%daily_amp_hours
sys.exit(0)



client.close()
