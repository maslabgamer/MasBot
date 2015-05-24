# -*- coding: utf-8 -*-
"""
Created on Thu May 21 20:05:25 2015
@author: Samuel
"""
#!/usr/bin/python
import socket, time, threading, mysql.connector, sys, Dice_Roller, Test_Module
from datetime import datetime
add_message = ("INSERT INTO messages (userTo, userFrom, message, messageSent) VALUES (%s, %s, %s, %s)")           
select_message = ("SELECT messageid, userTo, userFrom, message, messageSent FROM messages WHERE userTo=%s")
delete_message = ("DELETE FROM messages WHERE userTo=%s")

class IRC_Server:
    def __init__(self, host, port, nick, channel, owner, password=""):
        self.irc_host = host
        self.irc_port = port
        self.irc_nick = nick
        self.irc_channel = channel
        self.irc_current_channel = ""
        self.irc_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.is_connected = False
        self.should_reconnect = False
        self.owner = OWNER
        self.command = ""
        self.param = ""
        self.lName = ""
        self.lText = ""
        self.lFirstWord = ""
        self.UserList = {}
        self.Commands = {'roll': Dice_Roller.parse, 'test': Test_Module.call, 'tell': self.store_message}
        self.response = {'belgium': [1, 'gasps!'], 'kicks masbot': [2, 'Rude.']}
        
    def resCom(self):
        self.Commands = {'roll': Dice_Roller.parse, 'test': Test_Module.call, 'tell': self.store_message}
        
    def connect(self):
        self.should_reconnect = True
        self.irc_sock.connect((self.irc_host, self.irc_port))
        print ("Connected to: {0}:{1}".format(str(self.irc_host), str(self.irc_port)))
        self.irc_sock.send (("NICK {0} \r\n".format(self.irc_nick)).encode())
        print ("Setting bot nick to " + str(self.irc_nick) )
        self.irc_sock.send (("USER {0} 8 * :X\r\n".format(self.irc_nick)).encode())
        print ("Setting User")
        time.sleep(10)
        for u in self.irc_channel:
            self.join_channel(u)
        self.running()
        
    def join_channel(self, channel):
        self.irc_sock.send (("JOIN {0} \r\n".format(channel)).encode())
        
    def send_message(self, message):
        if message is not None: self.irc_sock.send('PRIVMSG {0} :{1}\r\n'.format(self.irc_current_channel, message))
        
    def getUserlist(self, c):
        self.irc_sock.send (("NAMES {0} \r\n".format(self.irc_current_channel)).encode())
    
    def getUsers(self, l):
        l = l.split('353')[1].split(':')[1].split(' ')
        for i, v in enumerate(l):
            v = v if v[0].isalpha() else v[1:]
            l[i] = v if '\r\n' not in v[-2:] else v[:-2]
        l.remove('MasBot')
        self.UserList[self.irc_current_channel] = l
        
    def getInfo(self, l):
        l = l.split(':', 2)
        getName = l[1].split('!')[0]
        self.lName = getName
        if len(l) > 2: 
            self.lText = l[2]
            if '#' in l[1]: self.irc_current_channel = '#{0}'.format(l[1].split('#')[1])
        self.lFirstWord = self.lText.split(' ')[0]
        if self.lFirstWord[0] == '.': 
            self.command = self.lFirstWord[1:]
        else: self.command = " "
        
    def makeReadable(self, l):
        return "{0}: {1}".format(self.lName, self.lText)
        
    def rel(self, t):
        mod = sys.modules.get(t.split(' ')[1].rstrip()) 
        mod = reload(mod)
        self.resCom()
        self.send_message('Module reloaded.')
        
    def store_message(self, l):
        db_cursor.execute(add_message, (l.split(' ', 1)[0], self.lName, l.split(' ', 1)[1][:-2], datetime.now()))
        messagesDB.commit()
        self.send_message("I'll let {0} know.".format(l.split(' ', 1)[0]))
        
    def parse_time(self, t):
        t = str(t).split('.')[0].split(':')
        timeM = ""
        if ',' in t[0]:
            days = t[0].split(',')
            days[1] = days[1].strip()
            t[0] = days[1]
            days = int(days[0].split(' ')[0])
            if days > 0: timeM += "{0} days, ".format(days)
        for i, v in enumerate(t):
            t[i] = int(v)
        if t[0] > 0: timeM += "{0} hours, ".format(t[0])
        if t[1] > 0: timeM += "{0} minutes, ".format(t[1])
        if len(timeM) > 0: timeM += "and "
        timeM += "{0} seconds ago.".format((t[2]))
        return timeM
        
    def messageCheck(self):
        db_cursor.execute(select_message, (self.lName,) )
        for(messageid, userTo, userFrom, message, messageSent) in db_cursor:
            self.send_message('{0}: {1} said "{2}" {3}'.format(self.lName, userFrom, message, self.parse_time(datetime.now() - messageSent)))            
        db_cursor.execute(delete_message, (self.lName,) )
        messagesDB.commit()
        
    def choose_response(self):
        for key in self.response:
            if key in self.lText.lower(): self.send_message('\x01ACTION {0}\x01'.format(self.response[key][1])) if self.response[key][0] == 1 else self.send_message(self.response[key][1])
                    
    def running(self):
        connected = True
        while connected:
            line = self.irc_sock.recv(4096) #recieve server messages
            self.getInfo(line)
            self.messageCheck()
            if 'PING' in line: # Call a parsingfunction
                self.irc_sock.send('PONG {0}n'.format(line.rstrip().split()[1]))
            elif self.command.strip() in self.Commands:
                self.send_message(self.Commands[self.command.strip()](self.lText.split(' ', 1)[1] if len(self.lText.split(' ', 1)) > 1 else ""))
            elif self.command == 'reload': self.rel(self.lText)
            elif '353' in line: self.getUsers(line)
            elif 'JOIN' in line: self.getUserlist(self.irc_current_channel)
            self.command = " "
            self.lFirstWord = " "
            print (self.makeReadable(line) if 'PRIVMSG' in line else line)
            self.choose_response()
        
HOST="irc.sorcery.net"
PORT=6667
NICK="MasBot"
IDENT="masbot"
REALNAME="MaslabsBot"
readbuffer=""
CHANLIST = ["#ucascadia"]
OWNER = "Maslab"
messagesDB = mysql.connector.connect(user='maslab', password='reallygood2468', host='127.0.0.1', port=3306, database='messageDB')
db_cursor = messagesDB.cursor()
connections = IRC_Server(HOST, PORT, NICK, CHANLIST, OWNER)
thr = threading.Thread(None, connections.connect)
thr.daemon = True
thr.start()