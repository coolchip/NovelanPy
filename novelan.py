#!/usr/bin/python3

import socket
import struct
from collections import namedtuple


class novelan:
    __host = "0.0.0.0"
    __port = 8888
    __sock = None

    def __init__(self, host, port=8888):
        self.__host = host
        self.__port = port

    def __connect(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect((self.__host, self.__port))

    def __read(self, command, fmt, tnames, containsstatus):
        recv_msg = bytearray()

        try:
            #connect
            self.__connect()
            
            #send
            msg = struct.pack("!II", command, 0 )
            totalsent = 0
            while totalsent < len(msg):
                sent = self.__sock.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent

            #receive
            data = self.__sock.recv(4)
            recv_command = struct.unpack("!I", data)[0]
            if recv_command != command:
                raise("received wrong command! ", command, recv_command)

            if containsstatus:
                data = self.__sock.recv(4)
                stat = struct.unpack("!I", data)[0]

            data = self.__sock.recv(4)
            remaining = struct.unpack("!I", data)[0] * 4    # datacount * len(int) = bytelength

            while remaining > 0:
                chunk = self.__sock.recv(remaining)
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                recv_msg.extend(chunk)
                remaining -= len(chunk)

        finally:
            self.__sock.close()

        if struct.calcsize(fmt) != len(recv_msg):
            raise("format size does not fit received bytes")
        return tnames._make(struct.unpack(fmt, recv_msg))


    def readStatus(self):
        fmt = '!40xiiiiiiiiiiiii4xiiiii108xiiiiiiiiiii336xiiiii108x'
        statustupel = namedtuple('status', 'temperature_supply temperature_return temperature_reference_return temperature_out_external temperature_hot_gas temperature_outside temperature_outside_avg temperature_servicewater temperature_servicewater_reference temperature_probe_in temperature_probe_out temperature_mk1 temperature_mk1_reference temperature_mk2 temperature_mk2_reference heatpump_solar_collector heatpump_solar_storage temperature_external_source hours_compressor1 starts_compressor1 hours_compressor2 starts_compressor2 hours_zwe1 hours_zwe2 hours_zwe3 hours_heatpump hours_heating hours_warmwater hours_cooling thermalenergy_heating thermalenergy_warmwater thermalenergy_pool thermalenergy_total massflow')
        status = self.__read(3004, fmt, statustupel, True)
        statusdict = status._asdict()
        for key in statusdict:
            print(key, statusdict[key])

    def readParameter(self):
        fmt = '!4xiiii412xi4xi84xi2868xii676x'
        parametertupel = namedtuple('parameter', 'heating_temperature warmwater_temperature heating_operation_mode warmwater_operation_mode cooling_operation_mode cooling_release_temperature cooling_inlet_temp cooling_start_after_hours cooling_stop_after_hours')
        parameter = self.__read(3003, fmt, parametertupel, False)
        paramdict = parameter._asdict()
        for key in paramdict:
            print(key, paramdict[key])

    def __write(self, param, value):
             #connect
            self.__connect()
            
            #send
            command = 3002
            msg = struct.pack("!III", command, param, value)
            print(msg)
            totalsent = 0
            while totalsent < len(msg):
                sent = self.__sock.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent

            #receive
            data = self.__sock.recv(4)
            recv_command = struct.unpack("!I", data)[0]
            if recv_command != command:
                raise("received wrong command! ", command, recv_command)

            data = self.__sock.recv(4)
            resp = struct.unpack("!I", data)[0]

            print("Response: ", resp)
            self.__sock.close()

    def writeHeatMode(self, value):
        param = 3
        self.__write(param, value)
        

if __name__ == '__main__':
    myPump = novelan(host="192.168.178.22")
    myPump.readStatus()
    myPump.readParameter()
    myPump.writeHeatMode(0)

