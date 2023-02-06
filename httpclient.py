#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Kezziah Ayuno
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return data[0].split(" ")[1]

    def get_headers(self,data):
        if data[0] == "GET":
            headers = "GET " + data[1] + " HTTP/1.1\r\n" + "Host: " + data[2] + "\r\n" + "Connection: close\r\n"
            if data[3] != None:
                headers += str(urllib.parse.urlencode(data[3])) + "\r\n\r\n"
            else: 
                headers += "\r\n"
        elif data[0] == "POST":
            headers = "POST " + data[1] + " HTTP/1.1\r\n" + "Host: " + data[2] \
            + "\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\nContent-Length: " 
            if data[3] != None: 
                headers += str(len(urllib.parse.urlencode(data[3]))) + "\r\n\r\n" + str(urllib.parse.urlencode(data[3]))
            else: 
                headers += "0\r\n\r\n"
        
        return headers

    def get_body(self, data):
        only_data = [] 
        for i in data:
            if i != "":
                only_data.append(i)
        return data[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = urllib.parse.urlparse(url).hostname, urllib.parse.urlparse(url).port, urllib.parse.urlparse(url).path
        
        if path == "": 
            path = "/"
        if port == None: 
            port = 80

        self.connect(host, port)

        to_send = self.get_headers(["GET", path, host, args])
        print(to_send)

        self.sendall(to_send)

        response = self.recvall(self.socket)
        response = response.split("\r\n")

        self.close()

        code = int(self.get_code(response))
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = urllib.parse.urlparse(url).hostname, urllib.parse.urlparse(url).port, urllib.parse.urlparse(url).path

        if path == "": 
            path = "/"
        if port == None: 
            port = 80
        
        self.connect(host, port)

        to_send = self.get_headers(["POST", path, host, args])

        self.sendall(to_send)

        response = self.recvall(self.socket)
        response = response.split("\r\n")

        self.close()

        code = int(self.get_code(response))
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
