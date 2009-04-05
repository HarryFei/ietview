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

import os
import re
import iet_target

class IetConfTarget(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.luns = {}
        self.users = {}
        self.options = {}

        for kw, val in kwargs.iteritems():
            self.options[kw] = val
        
    def add_lun(self, number, path, iotype, **kwargs):
        self.luns[number] = iet_target.IetLun(number, path, iotype, **kwargs)

    def add_user(self, uname, passwd):
        self.users[uname] = passwd

    def add_option(self, key, val):
        self.options[key] = val

    def write(self, f, prepend=''):
        f.write('%sTarget %s\n' % (prepend, self.name))

        for lun in self.luns.itervalues():
            lun.write(f, prepend)

        for user, passwd in self.users.iteritems():
            f.write('%s\tIncomingUser %s %s\n' % (prepend, user, passwd))

        for key, val in self.options.iteritems():
            if key != 'OutgoingUser':
                f.write('%s\t%s %s\n' % (prepend, key, val))
            else:
                f.write('%s\t%s %s\n' % 
                        (prepend, key, ' '.join(val.split('/'))))

class IetConfFile(object):
    TARGET_REGEX='Target\s+(?P<target>\S+)'
    CMNT_TARGET_REGEX='\s*#\s*Target\s+(?P<target>\S+)'
    LUN_REGEX='Lun\s+(?P<lun>\d+)\s+Path=(?P<path>[^ \t\n\r\f\v,]+)\s*,\s*Type\s*=\s*(?P<iotype>[^ \t\n\r\f\v,]+)(?P<options>\S+)?'
    OPTION_REGEX='[^a-zA-Z]*(?P<key>\S+)\s+(?P<value>\S+)'
    IN_USERPASS_REGEX='\s*IncomingUser\s+(?P<uname>\S+)\s+(?P<pass>\S+)'
    OUT_USERPASS_REGEX='\s*OutgoingUser\s+(?P<uname>\S+)\s+(?P<pass>\S+)'

    possible_options = [
        'OutgoingUser',
        'Alias',
        'MaxConnections',
        'ImmediateData',
        'MaxRecvDataSegmentLength',
        'MaxXmitDataSegmentLength',
        'MaxBurstLength',
        'FirstBurstLength',
        'DefaultTime2Wait',
        'DefaultTime2Retain',
        'MaxOutstandingR2T',
        'DataPDUInOrder',
        'DataSequenceInOrder',
        'ErrorRecoveryLevel',
        'HeaderDigest',
        'DataDigest',
        'Wthreads',
        'iSNSServer',
        'iSNSAccessControl']

    def __init__(self, filename):
        self.targets = {}
        self.users = {}
        self.options = {}
        self.inactive_targets = {}
        self.filename = filename

    def add_target(self, name, active, **kwargs):
        if active:
            self.targets[name] = IetConfTarget(name, **kwargs)
        else:
            self.inactive_targets[name] = IetConfTarget(name, **kwargs)

    def activate_target(self, target):
        local_target = self.inactive_targets[target.name]
        self.targets[target.name] = local_target
        del self.inactive_targets[target.name]

    def disable_target(self, target):
        local_target = self.targets[target.name]
        self.inactive_targets[target.name] = local_target
        del self.targets[target.name]

    def delete_target(self, name, active):
        if active:
            del self.targets[name]
        else:
            del self.inactive_targets[name]

    def write(self):
        f = file(self.filename, 'w')

        f.write('# Written by IETView\n')
        f.write('# Global discovery options\n')
        for key, val in self.options.iteritems():
            if key != 'OutgoingUser':
                f.write('%s %s\n' % (key, val))
            else:
                f.write('%s %s\n' % (key, ' '.join(val.split('/'))))

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

    def parse_file(self):
        if os.path.exists(self.filename):
            f = file(self.filename, 'r')
        else:
            return

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
                new_lun = iet_target.IetLun(int(m.group('lun')),
                        m.group('path'), m.group('iotype'))

                new_lun.add_options(m.group('options'))
        
                current_target.luns[new_lun.number] = new_lun
        
                continue
        
                   
            m = re.search(self.IN_USERPASS_REGEX, line)
            if m:
                if current_target:
                    current_target.users[m.group('uname')] = m.group('pass')
                else:
                    self.users[m.group('uname')] = m.group('pass')

                continue
 
            m = re.search(self.OUT_USERPASS_REGEX, line)
            if m:
                if current_target:
                    current_target.options['OutgoingUser'] = '%s/%s' % \
                            (m.group('uname'), m.group('pass'))
                else:
                    self.options['OutgoingUser'] = '%s/%s' % \
                            (m.group('uname'), m.group('pass'))

                continue

            m = re.search(self.OPTION_REGEX, line)
            if m:
                if m.group('key') not in self.possible_options:
                    continue

                if current_target:
                    current_target.options[m.group('key')] = m.group('value')
                else:
                    self.options[m.group('key')] = m.group('value')

                continue
        
        f.close()

    def update(self, target, diff):
        if target.active:
            local_target = self.targets[target.name]
        else:
            local_target = self.inactive_targets[target.name]

        for op, type, val in diff:
            if type == 'name':
                old_name = local_target.name
                local_target.name = val

                if target.active:
                    self.targets[val] = local_target
                    del self.targets[old_name]
                else:
                    self.inactive_targets[val] = local_target
                    del self.inactive_targets[old_name]
            elif type == 'option':
                key, val = val.split('=')

                if op == iet_target.IetTarget.ADD:
                    local_target.add_option(key, val)
                elif op == iet_target.IetTarget.UPDATE:
                    local_target.options[key] = val
            elif type == 'lun':
                if op == iet_target.IetTarget.ADD:
                    local_target.add_lun(val.number, val.path, val.iotype, **val.options)
                elif op == iet_target.IetTarget.DELETE:
                    del local_target.luns[val.number]
                elif op == iet_target.IetTarget.UPDATE:
                    del local_target.luns[val.number]
                    local_target.add_lun(val.number, val.path, val.iotype, **val.options)
            elif type == 'user':
                uname, passwd = val.split('/')

                if op == iet_target.IetTarget.ADD:
                    local_target.add_user(uname, passwd)
                elif op == iet_target.IetTarget.DELETE:
                    del local_target.users[uname]
                elif op == iet_target.IetTarget.UPDATE:
                    local_target.users[uname] = passwd

