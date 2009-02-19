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
import iet_target

class IetAllowDeny(object):
    ALLOWDENY_REGEX='\s*(?P<target>\S+)\s+(?P<hosts>.+)'
    def __init__(self):
        self.targets = {}

    def parse(self, filename):
        f = open(filename, 'r')

        for line in f:
            if re.match('\s*#', line): continue

            m = re.match(self.ALLOWDENY_REGEX, line)

            if m:
                hosts = re.split('\s*,\s*', m.group('hosts'))
                self.targets[m.group('target')] = hosts

        f.close

    def add_host(self, target, host):
        if target not in self.targets:
            self.targets[target] = []

        if host not in self.targets[target]:
            self.targets[target].append(host)

    def update(self, target, diff, my_type):
        for op, type, val in diff:
            if type == 'name':
                host_list = self.targets[target.name]
                self.targets[val] = host_list
                del self.targets[target.name]
            elif type == my_type:
                if op == iet_target.IetTarget.ADD:
                    if target.name not in self.targets:
                        self.targets[target.name] = []

                    self.targets[target.name].append(val)
                elif op == iet_target.IetTarget.DELETE:
                    self.targets[target.name].remove(val)
    
    def write(self, filename):
        f = open(filename, 'w')

        for target, hosts in self.targets.iteritems():
            f.write('%s %s\n' % (target, ', '.join(hosts)))

        f.close()

    def dump(self):
        for key, value in self.targets.iteritems():
            print key, '=', value

