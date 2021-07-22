# -*- coding: utf-8 -*-
import math
import time
from informer.config import MAX_LENGTH

def create_head(data, length=8):
    data_str = str(data)
    return '0'*(length-len(data_str)) + data_str

def send_simple_package(data, socket, address, port, debug=False):
    ret = socket.sendto(data,(address,port))
    if debug:
        print('Simple send', data)
    return ret
    
def send_package(data, socket, address, port, timestamp=None, debug=False):
    if timestamp is None:
        _timestamp = int(round(time.time()*1000*1000))
    else:
        _timestamp = int(round(timestamp*1000*1000))
    timestamp_head = bytes(str(_timestamp), 'utf-8')
        
    length = len(data)
    length_head = create_head(length)

    package_remain =  math.ceil(length/MAX_LENGTH)
    send_id = 0
    while package_remain > 0:
        package_head = create_head(package_remain-1)
        if package_remain > 1:
            send_data =  bytes(package_head + length_head, 'utf-8') + timestamp_head + data[send_id*MAX_LENGTH:(send_id+1)*MAX_LENGTH]
        else:
            send_data = bytes(package_head + length_head, 'utf-8') + timestamp_head + data[send_id*MAX_LENGTH:]

        ret = socket.sendto(send_data,(address,port))
        if ret != len(send_data):
            continue
        if debug:
            print('Send', str(len(send_data)), 'Bytes, ', str(send_id+1), '/', str(math.ceil(length/MAX_LENGTH)))
        send_id += 1
        package_remain -= 1