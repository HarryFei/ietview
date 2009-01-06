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
import subprocess

class IetAdm(object):
    def __init__(self):
        pass

    def show(self, params, tid, sid=-1):
        if sid >= 0:
            process = subprocess.Popen('ietadm --op=show --tid=%d --sid=%d' % (tid, sid), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        else:
            process = subprocess.Popen('ietadm --op=show --tid=%d' % tid, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            return process.returncode 

        for line in process.stdout:
            m = re.match('([^=]+)=(.+)', line)
            if m:
                params[m.group(1)] = m.group(2)

        return 0

    def add_target(self, tid, name):
        process = subprocess.Popen('ietadm --op=new --tid=%d --params Name=%s' % (tid, name), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        process.wait()

        if process.returncode != 0:
            return process.returncode 

        return 0

    def add_lun(self, tid, lun, path, type):
        process = subprocess.Popen('ietadm --op=new --tid=%d --lun=%d --params=Path=%s,Type=%s' % (tid, lun, path, type), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        process.wait()

        if process.returncode != 0:
            return process.returncode 

        return 0

    def add_option(self, tid, key, value):
        if key == 'OutgoingUser':
            process = subprocess.Popen('ietadm --op=new --tid=%d --user --params=OutgoingUser=%s,Password=%s' % (tid, key, value), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        else:
            process = subprocess.Popen('ietadm --op=update --tid=%d --params=%s=%s' % (tid, key, value), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            return process.returncode 

        return 0

    def add_user(self, tid, uname, passwd):
        process = subprocess.Popen('ietadm --op=new --tid=%d --user --params=IncomingUser=%s,Password=%s' % (tid, uname, passwd), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        process.wait()

        if process.returncode != 0:
            return process.returncode 

        return 0

    def delete_target(self, tid):
        process = subprocess.Popen('ietadm --op=delete --tid=%d' % tid, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        process.wait()

        if process.returncode != 0:
            return process.returncode 

        return 0



