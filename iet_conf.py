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

class IetConfLun(object):
    def __init__(self, number, path, type, **kwargs):
        self.number = number
        self.type = type
        self.path = path
        
    def write(self, f, prepend=''):
        f.write('%s\tLun %d Path=%s,Type=%s\n'
                % (prepend, self.number, self.path, self.type))


class IetConfTarget(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.luns = {}
        self.users = {}
        self.options = []

        for kw, val in kwargs.iteritems():
            options.append((kw, val))
        
    def add_lun(self, number, path, type, **kwargs):
        self.luns[number] = IetConfLun(number, path, type, **kwargs)

    def add_user(self, uname, passwd):
        self.users[uname] = passwd

    def write(self, f, prepend=''):
        f.write('%sTarget %s\n' % (prepend, self.name))

        for lun in self.luns.itervalues():
            lun.write(f, prepend)

        for user, passwd in self.users.iteritems():
            f.write('%s\tIncomingUser %s %s\n' % (prepend, user, passwd))

        for key, val in self.options:
            if type(val) == str:
                f.write('%s\t%s %s\n' % (prepend, key, val))
            else:
                f.write('%s\t%s %s\n' % (prepend, key, ' '.join(val)))

class IetConfFile(object):
    TARGET_REGEX='Target\s+(?P<target>\S+)'
    CMNT_TARGET_REGEX='\s*#\s*Target\s+(?P<target>\S+)'
    LUN_REGEX='Lun\s+(?P<lun>\d+)\s+Path=(?P<path>[^ \t\n\r\f\v,]+)\s*,\s*Type\s*=\s*(?P<iotype>\w+)'
    OPTION_REGEX='\s*(?P<key>\S+)\s+(?P<value>\S+)'
    USERPASS_REGEX='\s*(?P<key>\S+)\s+(?P<uname>\S+)\s+(?P<pass>\S+)'
    IN_USERPASS_REGEX='\s*IncomingUser\s+(?P<uname>\S+)\s+(?P<pass>\S+)'
    OUT_USERPASS_REGEX='\s*OutgoingUser\s+(?P<uname>\S+)\s+(?P<pass>\S+)'

    def __init__(self):
        self.targets = {}
        self.users = {}
        self.options = []
        self.inactive_targets = {}

    def add_target(self, name, **kwargs):
        self.targets[name] = IetConfTarget(name, **kwargs)

    def write(self, filename):
        f = file(filename, 'w')

        f.write('# Written by IETView.py\n')
        f.write('# Global discovery options\n')
        for key, val in self.options:
            if type(val) == str:
                f.write('%s %s\n' % (key, val))
            else:
                f.write('%s %s\n' % (key, ' '.join(val)))

        f.write('\n')

        f.write('# Global discovery users\n')    
        for user, passwd in self.users.iteritems():
            f.write('IncomingUser %s %s\n' % (user, passwd))

        f.write('\n')

        f.write('# Active targets\n')
        for target in self.targets.itervalues():
            target.write(f)
            f.write('\n')

        f.write('# Inactive targets\n')
        for target in self.inactive_targets.itervalues():
            target.write(f, prepend='#')
            f.write('\n')

        f.close()

    def parse(self, filename):
        f = file(filename, 'r')

        # state = -1: haven't seen a target yet
        # state = 0: active (uncommented) target
        # state = 1: inactive (commented) target
        state = -1 
        current_target = None

        #TODO: Deal with split lines.
        for line in f:
            m = re.search(self.CMNT_TARGET_REGEX, line)
            if m:
                current_target = IetConfTarget(m.group('target'))
                self.inactive_targets[current_target.name] = current_target
                state = 1
                continue

            # Ignore any commented out lines in active targets
            if state < 1 and '#' in line:
                continue

            #TODO: Make case insensitive
            m = re.search(self.TARGET_REGEX, line)
            if m:
                current_target = IetConfTarget(m.group('target'))
                self.targets[current_target.name] = current_target
                state = 0
                continue

            #TODO: Make case insensitive
            m = re.search(self.LUN_REGEX, line)
            if m:
                new_lun = IetConfLun(int(m.group('lun')), m.group('path'),
                                     m.group('iotype'))
        
                current_target.luns[new_lun.number] = new_lun
        
                continue
        
                   
            m = re.match(self.IN_USERPASS_REGEX, line)
            if m:
                if current_target:
                    current_target.users[m.group('uname')] = m.group('pass')
                else:
                    self.users[m.group('uname')] = m.group('pass')

                continue
 
            m = re.match(self.OUT_USERPASS_REGEX, line)
            if m:
                if current_target:
                    current_target.options.append(('OutgoingUser', (m.group('uname'), m.group('pass'))))
                else:
                    self.options.append(('OutgoingUser', (m.group('uname'),
                                                    m.group('pass'))))

                continue

            m = re.match(self.OPTION_REGEX, line)
            if m:
                if current_target:
                    current_target.options.append((m.group('key'), m.group('value')))
                else:
                    self.options.append((m.group('key'), m.group('value')))

                continue
        
        f.close()

