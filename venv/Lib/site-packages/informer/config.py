# -*- coding: utf-8 -*-

MAX_LENGTH = 65535 - 16*4

PUBLICT_IP = '127.0.0.1'#'47.100.46.11'

PORT_DICT = {
        'vision':10001,
        'sensor':10002,
        'cmd':10003,
        'debug':10004,
        'clock':10005,
        'message':10006,
        #'sim':10007,
        }

RECV_KEYS = ['cmd', 'message', 'sim', 'clock']

REGISTER_KEYS = list(PORT_DICT.keys())

colors = ['black','white','darkGray','gray','lightGray','red','green','blue','cyan','magenta','yellow','darkRed','darkGreen','darkBlue','darkCyan','darkMagenta','darkYellow']
