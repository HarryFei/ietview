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
import iet_target

class IetVolume(object):
    def __init__(self, tid, target):
        self.tid = tid
        self.target = target

        self.luns = {}

    def add_lun(self, lun):
        self.luns[lun.number] = lun

class IetVolumes(object):
    TARGET_REGEX='tid:(?P<tid>\d+)\s+name:(?P<target>.+)'
    LUN_REGEX='lun:(?P<lun>\d+)\s+state:(?P<state>\d+)\s+iotype:(?P<iotype>\w+)\s+iomode:(?P<iomode>\w+)\s+path:(?P<path>.+)'
    def __init__(self):
        self.volumes = {}

    def parse(self, filename):
        f = file(filename, "r")

        tv = None

        for line in f:
            m = re.search(self.TARGET_REGEX, line)
            if m:
                tv = IetVolume(int(m.group('tid')), m.group('target'))
                self.volumes[tv.tid] = tv
        
            m = re.search(self.LUN_REGEX, line) 

            if m:
                tv.add_lun(iet_target.IetLun(number=int(m.group('lun')),
                    state=int(m.group('state')),
                    iotype=m.group('iotype'), iomode=m.group('iomode'),
                    path=m.group('path')))

        f.close()

