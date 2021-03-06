#!/usr/bin/python3

from novelan import novelan
 
if __name__ == '__main__':
    myPump = novelan(host="192.168.178.22")

    statusdict = myPump.readStatus()
    paramdict = myPump.readParameter()

    for key in statusdict:
        print(key, statusdict[key])

    print("\n")

    for key in paramdict:
        print(key, paramdict[key])

    print("\n")

    outsideTemperature = str(myPump.readStatusValue("temperature_outside"))
    print("Draußen sind es " + outsideTemperature + "°C.")

#    myPump.writeHeatingMode(novelan.OPERATING_MODE_OFF)

