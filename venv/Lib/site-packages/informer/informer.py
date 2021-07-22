# -*- coding: utf-8 -*-
import json
import socket
import threading
from time import sleep
from informer.network import send_package, send_simple_package
import informer.utils as utils
from informer import config

class Informer():
    def __init__(self, robot_id=None, block=True):
        self.robot_id = str(robot_id) if robot_id != None else None
        self.block = block
        self.register_keys = config.REGISTER_KEYS
        self.port_dict = config.PORT_DICT
        self.recv_keys = config.RECV_KEYS
        self.socket_dict = {}
        self.data_dict = {}
        self.connect_state = {}
        # register IP and port
        for key in self.register_keys:
            self.socket_dict[key] = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            if self.robot_id == None:
                self.data_dict[key] = ('server:'+key).encode("utf-8")
            else:
                self.data_dict[key] = utils.encode_message(
                        data='server:'+key,
                        robot_id = self.robot_id,
                        mtype='register',
                        pri=5)
            self.socket_dict[key].sendto(self.data_dict[key], (config.PUBLICT_IP, self.port_dict[key]))
        # temp threads to receive start packages
        for key in self.register_keys:
            recv_thread = threading.Thread(
                    target=self.connect, args=(key, self.socket_dict[key])
                    )
            recv_thread.start()
            
        # wait for connecting
        if self.block:
            while set(self.register_keys) != set(self.connect_state.keys()):
                sleep(0.001)
        print('start to work...')
            
        # start receive threads
        for key in self.recv_keys:
            if key in self.register_keys:
                try:
                    receive_func = getattr(self.__class__, key+'_recv')
                except AttributeError:
                    print(self.__class__.__name__, 'has no attribute called', key+'_recv')
                    continue
                recv_thread = threading.Thread(
                    target = receive_func, args=(self,)
                )
                recv_thread.start()

        # debug info
        self.cnt = 0
        self.debug_dict = {}
        self.sim_info = None
        
    def connect(self, key, sock):
        data = ''
        while len(data) < 1:
        	data, address = sock.recvfrom(65535)
        data = str(data, encoding = "utf-8")
        try:
            json_data = json.loads(data)
            ip = json_data['Data'].split(':')[0]
            port = int(json_data['Data'].split(':')[1])
            print('Get IP/port', ip, ':', port, 'as', key)
            self.connect_state[key] = True
        except:
            print('Error when connect', key, '.\tGet', data)
    
    def send_vision(self, img, isGrey=False, timestamp=None, debug=False):
        data = utils.encode_img(img, isGrey)
        send_package(data, self.socket_dict['vision'], config.PUBLICT_IP, self.port_dict['vision'], debug=debug, timestamp=timestamp)
    
    def send_sensor_data(self, v, w, c, debug=False):
        data = utils.encode_sensor(v, w, c)
        send_simple_package(data, self.socket_dict['sensor'], config.PUBLICT_IP, self.port_dict['sensor'], debug=debug)
        
    def draw_box(self, lt_x, lt_y, width, height, message='', color='red', **kwargs):
        data = utils.to_json(dtype='box',
                       lt_x=lt_x, lt_y=lt_y, width=width, height=height,
                       message=message,
                       color=color)
        self.debug_dict[str(self.cnt)] = data
        self.cnt += 1
        
    def draw_center_box(self, ct_x, ct_y, width, height, message='', color='red'):
        data = utils.to_json(dtype='center_box',
                       ct_x=ct_x, ct_y=ct_y, width=width, height=height,
                       message=message,
                       color=color)
        self.debug_dict[str(self.cnt)] = data
        self.cnt += 1
        
    def draw_line(self, s_x, s_y, e_x, e_y, color='red'):
        data = utils.to_json(dtype='line',
                       s_x=s_x, s_y=s_y, e_x=e_x, e_y=e_y,
                       color=color)
        self.debug_dict[str(self.cnt)] = data
        self.cnt += 1
        
    def clear(self):
        data = utils.to_json(dtype='clear')
        self.debug_dict[str(self.cnt)] = data
        self.cnt += 1
        
    def draw(self):
        data = utils.encode_debug_message(self.debug_dict)
        self.debug_dict = {}
        self.cnt = 0
        send_simple_package(data, self.socket_dict['debug'], config.PUBLICT_IP, self.port_dict['debug'])
        
    def send_message(self, data, mtype='normal', pri=5, debug=False):
        data = utils.encode_message(data, self.robot_id, mtype, pri)
        send_simple_package(data, self.socket_dict['message'], config.PUBLICT_IP, self.port_dict['message'], debug=debug)
        
    def send_sim(self, v, w):
        data = {"v":v, "w":w}
        data = utils.encode_message(data, self.robot_id, mtype='cmd', pri=5)
        send_simple_package(data, self.socket_dict['sim'], config.PUBLICT_IP, self.port_dict['sim'])
        
    def send_sim_goal(self, x, y):
        data = {"x":x, "y":y}
        data = utils.encode_message(data, self.robot_id, mtype='goal', pri=5)
        send_simple_package(data, self.socket_dict['sim'], config.PUBLICT_IP, self.port_dict['sim'])
        
    def clock_recv(self):
        while True:
            data, addr = self.socket_dict['clock'].recvfrom(65535)
            new_data = bytes(str(int(data)-1), 'utf-8')
            send_package(new_data, self.socket_dict['clock'], config.PUBLICT_IP, self.port_dict['clock'])
            
    def cmd_recv(self):
        while True:
            data,addr = self.socket_dict['cmd'].recvfrom(65535)
            json_data = json.loads(data.decode('utf-8'))
            self.parse_cmd(json_data)
            
    def parse_cmd(self, cmd):
        pass
        
    def message_recv(self):
        while True:
            data,addr = self.socket_dict['message'].recvfrom(65535)
            json_data = json.loads(data.decode('utf-8'))
            self.parse_message(json_data)
            
    def parse_message(self, message):
        message_type = message['Mtype']
        pri = message['Pri']
        robot_id = message['Id']
        data = message['Data']
        #print(message_type, pri, robot_id, data)
        
    def sim_recv(self):
        while True:
            data,addr = self.socket_dict['sim'].recvfrom(65535)
            json_data = json.loads(data.decode('utf-8'))
            self.parse_sim(json_data)
            
    def parse_sim(self, message):
        #message_type = message['Mtype']
        #pri = message['Pri']
        #robot_id = message['Id']
        data = message['Data']
        self.sim_info = data
        
    def get_sim_info(self):
        return self.sim_info
        