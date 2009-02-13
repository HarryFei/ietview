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

class IetSession(object):
    def __init__(self, tid, target):
        self.tid = tid
        self.target = target
    
        self.clients = {}

class IetInitiatorClient(object):
    def __init__(self, sid, initiator):
        self.sid = sid
        self.initiator = initiator
        self.cid = -1
        self.ip = ""
        self.state = ""
        self.hd = ""
        self.dd = ""

    def set_cid(self, cid, ip, state, hd, dd):
        self.cid = cid
        self.ip = ip
        self.state = state
        self.hd = hd
        self.dd = dd

class IetSessions(object):
    TARGET_REGEX='tid:(?P<tid>\d+)\s+name:(?P<target>.+)'
    INITIATOR_REGEX='sid:(?P<sid>\d+)\s+initiator:(?P<init>.+)'
    CLIENT_REGEX='cid:(?P<cid>\d+)\s+ip:(?P<ip>[0-9\.]+)\s+state:(?P<state>\w+)\s+hd:(?P<hd>\w+)\s+dd:(?P<dd>\w+)'

    def __init__(self):
        self.sessions = {}

    def parse(self, filename):
        f = file(filename, 'r')

        session = None
        client = None

        for line in f:
            m = re.search(self.TARGET_REGEX, line)
            if m:
                session = IetSession(int(m.group('tid')),
                                     m.group('target'))

                self.sessions[session.target] = session
                continue
        
            m = re.search(self.INITIATOR_REGEX, line)
            if m:
                client = IetInitiatorClient(int(m.group('sid')),
                                            m.group('init'))

                continue
        
            m = re.search(self.CLIENT_REGEX, line)
            if m:
                client.set_cid(int(m.group('cid')), m.group('ip'),
                                   m.group('state'), m.group('hd'),
                                   m.group('dd'))
        
                session.clients[client.initiator] = client

                continue
                
        f.close()
        
     
    def dump(self):        
        for session in self.sessions.itervalues():
            print session.tid, session.target
            for client in session.clients:
                print client.sid, client.initiator, client.cid, client.ip,\
                      client.state, client.hd, client.dd
        
