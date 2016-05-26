#!/usr/bin/python3

import socket
import struct
from collections import namedtuple


def read(command, format, tnames, containsstatus):
    host = "192.168.178.22"
    port = 8888
    recv_msg = bytearray()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        #send
        msg = struct.pack("!II", command, 0 )
        totalsent = 0
        while totalsent < len(msg):
            sent = sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

        #receive
        data = sock.recv(4)
        recv_command = struct.unpack("!I", data)[0]
        if recv_command != command:
            raise("received wrong command! ", command, recv_command)

        if containsstatus:
            data = sock.recv(4)
            stat = struct.unpack("!I", data)[0]

        data = sock.recv(4)
        remaining = struct.unpack("!I", data)[0] * 4    # datacount * len(int) = bytelength

        while remaining > 0:
            chunk = sock.recv(remaining)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            recv_msg.extend(chunk)
            remaining -= len(chunk)

    finally:
        sock.close()

    if struct.calcsize(format) != len(recv_msg):
        raise("format size does not fit received bytes")
    return tnames._make(struct.unpack(fmt, recv_msg))


if __name__ == '__main__':
    fmt = '!40xiiiiiiiiiiiii4xiiiii108xiiiiiiiiiii336xiiiii108x'
    statustupel = namedtuple('status', 'temperature_supply temperature_return temperature_reference_return temperature_out_external temperature_hot_gas temperature_outside temperature_outside_avg temperature_servicewater temperature_servicewater_reference temperature_probe_in temperature_probe_out temperature_mk1 temperature_mk1_reference temperature_mk2 temperature_mk2_reference heatpump_solar_collector heatpump_solar_storage temperature_external_source hours_compressor1 starts_compressor1 hours_compressor2 starts_compressor2 hours_zwe1 hours_zwe2 hours_zwe3 hours_heatpump hours_heating hours_warmwater hours_cooling thermalenergy_heating thermalenergy_warmwater thermalenergy_pool thermalenergy_total massflow')
    status = read(3004, fmt, statustupel, True)
    statusdict = status._asdict()
    for key in statusdict:
        print(key, statusdict[key])

    fmt = '!4xiiii412xi4xi84xi2868xii676x'
    parametertupel = namedtuple('parameter', 'heating_temperature warmwater_temperature heating_operation_mode warmwater_operation_mode cooling_operation_mode cooling_release_temperature cooling_inlet_temp cooling_start_after_hours cooling_stop_after_hours')
    parameter = read(3003, fmt, parametertupel, False)
    paramdict = parameter._asdict()
    for key in paramdict:
        print(key, paramdict[key])
