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

class target_lun:
    def __init__(self, l, s, it, im, p):
        self.lun = l
        self.state = s
        self.iotype = it
        self.iomode = im
        self.path = p

class target_volume:
    def __init__(self, t, n):
        self.tid = t
        self.name = n

        self.luns = {}

    def add_lun(self, l):
        self.luns[l.lun] = l

class target_volumes:
    def __init__(self):
        self.volumes = {}

    def parse(self, filename):
        f = file(filename, "r")

        tv = None

        for line in f:
            m = re.search("tid:(\d+)\s+name:(.+)", line)
            if m:
                tv = target_volume(int(m.group(1)), m.group(2))
                self.volumes[tv.tid] = tv
        
            m = re.search("lun:(\d+)\s+state:(\d+)\s+iotype:(\w+)\s+iomode:(\w+)\s+path:(.+)", line) 

            if m:
                tv.add_lun(target_lun(int(m.group(1)), int(m.group(2)), m.group(3), m.group(4), m.group(5)))

        f.close()


