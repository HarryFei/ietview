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

class IETConfLun:
    def __init__(self, number, path, type, **kwargs):
        self.number = number
        self.type = type
        self.path = path
        
    def write(self, f):
        f.write('\tLun %d Path=%s,Type=%s\n' % (self.number, self.path, self.type))

class IETConfTarget:
    def __init__(self, name, **kwargs):
        self.name = name
        self.luns = {}
        self.options = {}

        for kw in kwargs: options[kw] = kwargs[kw]
        
    def add_lun(self, number, path, type, **keys):
        self.luns[number] = IETConfLun(number, path, type, **kwargs)

    def write(self, f):
        f.write('Target %s\n' % self.name)

        for lun in self.luns.itervalues():
            lun.write(f)

        for key, val in self.options.iteritems():
            f.write('\t%s %s\n' % (key, ' '.join(val)))

class IETConfFile:
    def __init__(self):
        self.targets = {}
        self.options = {}

    def add_target(self, name, **kwargs):
        self.targets[name] = IETConfTarget(name, **kwargs)

    def write(self, filename):
        f = file(filename, 'w')

        for key, val in self.options.iteritems():
            f.write('%s %s\n' % (key, ' '.join(val)))

        for target in self.targets.itervalues():
            target.write(f)

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
                current_target = IETConfTarget(m.group(1))
                continue

            #TODO: Make case insensitive
            m = re.search("Lun\s+(\d+)\s+Path=([^ \t\n\r\f\v,]+)\s*,\s*Type\s*=\s*(\w+)", line)
            if m:
                new_lun = IETConfLun(int(m.group(1)), m.group(2), m.group(3))
        
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

