#!/usr/bin/python

# This file is part of IETView
#
# IETView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IETView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IETView.  If not, see <http://www.gnu.org/licenses/>.

import re

class iet_session:
    def __init__(self, t, n):
        self.tid = t
        self.name = n
    
        self.session_list = []

class iet_client_session:
    def __init__(self, s, i):
        self.sid = s
        self.initiator = i
        self.cid = -1
        self.ip = ""
        self.state = ""
        self.hd = ""
        self.dd = ""

    def set_cid(self, c, i, s, h, d):
        self.cid = c
        self.ip = i
        self.state = s
        self.hd = h
        self.dd = d

class iet_sessions:
    def __init__(self):
        self.sessions = []

    def parse(self, filename):
        f = file(filename, 'r')

        current_session = None
        current_client = None

        for line in f:
            m = re.search("tid:(\d+)\s+name:(.+)", line)
            if m:
                if current_session: self.sessions.append(current_session)
        
                current_session = iet_session(int(m.group(1)), m.group(2))
                continue
        
            m = re.search("sid:(\d+)\s+initiator:(.+)", line)
            if m:
                current_client = iet_client_session(int(m.group(1)), m.group(2))
                continue
        
            m = re.search("cid:(\d+)\s+ip:([0-9\.]+)\s+state:(\w+)\s+hd:(\w+)\s+dd:(\w+)", line)
            if m:
                current_client.set_cid(int(m.group(1)), m.group(2), m.group(3),
                        m.group(4), m.group(5))
        
                current_session.session_list.append(current_client)
                continue
                
        f.close()
        
        if current_session: self.sessions.append(current_session)

     
    def dump(self):        
        for session in self.sessions:
            print session.tid, session.name
            for client in session.session_list:
                print client.sid, client.initiator, client.cid, client.ip, client.state, client.hd, client.dd
        
