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

class iet_conf_lun:
    def __init__(self, n, p, t):
        self.number = n
        self.type = t
        self.path = p
        
    def write(self, file):
        pass

class iet_conf_target:
    def __init__(self, n):
        self.name = n
        self.luns = {}
        self.options = {}

    def write(self, file):
        pass

class iet_conf_file:
    def __init__(self):
        self.targets = {}
        self.options = {}

    def write(self, filename):
        for key, val in self.options.iteritems():
            print key, ' '.join(val)
        for name, target in self.targets.iteritems():
            print 'Target', target.name
            for number, lun in target.luns.iteritems():
                print '\tLun %d Path=%s,Type=%s' % (lun.number, lun.path, lun.type)
            for key, val in target.options.iteritems():
                print '\t%s %s' % (key, ' '.join(val))

    def parse(self, filename):
        f = file(filename, 'r')

        state = 0 
        current_target = None

        #TODO: Deal with split lines.
        for line in f:
            if '#' in line: continue

            #TODO: Make case insensitive
            m = re.search("Target\s+(\S+)", line)

            if m:
                if current_target: self.targets[current_target.name] = current_target
                current_target = iet_conf_target(m.group(1))
                continue

            #TODO: Make case insensitive
            m = re.search("Lun\s+(\d+)\s+Path=([^ \t\n\r\f\v,]+)\s*,\s*Type\s*=\s*(\w+)", line)
            if m:
                new_lun = iet_conf_lun(int(m.group(1)), m.group(2), m.group(3))
        
                current_target.luns[new_lun.number] = new_lun
        
                continue
        
            m = re.match('\s*(\S+)\s+(\S+)', line)
            if m:
                if current_target:
                    current_target.options[m.group(1)] = m.group(2)
                else:
                    self.options[m.group(1)] = m.group(2)
                    
            m = re.match('\s*(\S+)\s+(\S+)\s+(\S+)', line)
            if m:
                if current_target:
                    current_target.options[m.group(1)] = (m.group(2), m.group(3))
                else:
                    self.options[m.group(1)] = (m.group(2), m.group(3))
        
        f.close()

        if current_target: self.targets[current_target.name] = current_target

