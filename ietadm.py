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
            cmnd = 'ietadm --op=show --tid=%d --sid=%d' % (tid, sid)
        else:
            cmnd = 'ietadm --op=show --tid=%d' % tid

        process = subprocess.Popen(cmnd, stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            print 'IETADM error:'
            for line in process.stdout:
                print '\t', line,
            print 'Command was:', cmnd 

            return process.returncode 

        for line in process.stdout:
            m = re.match('([^=]+)=(.+)', line)
            if m:
                params[m.group(1)] = m.group(2)

        return 0

    def add_target(self, tid, name):
        cmnd = 'ietadm --op=new --tid=%d --params Name=%s' % (tid, name)

        process = subprocess.Popen(cmnd, stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE, shell=True)
        process.wait()

        if process.returncode != 0:
            print 'IETADM error:'
            for line in process.stdout:
                print '\t', line,
            print 'Command was:', cmnd 

            return process.returncode 

        return 0

    def add_lun(self, tid, lun, path, type):
        cmnd = 'ietadm --op=new --tid=%d --lun=%d --params=Path=%s,Type=%s' \
                % (tid, lun, path, type)

        process = subprocess.Popen(cmnd, stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            print 'IETADM error:'
            for line in process.stdout:
                print '\t', line,
            print 'Command was:', cmnd 

            return process.returncode 

        return 0

    def add_option(self, tid, key, value):
        if key == 'OutgoingUser':
            cmnd = 'ietadm --op=new --tid=%d --user --params=OutgoingUser=%s,Password=%s' % (tid, key, value)
        else:
            cmnd = 'ietadm --op=update --tid=%d --params=%s=%s' \
                    % (tid, key, value)

        process = subprocess.Popen(cmnd, stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            print 'IETADM error:'
            for line in process.stdout:
                print '\t', line,
            print 'Command was:', cmnd 

            return process.returncode 

        return 0

    def add_user(self, tid, uname, passwd):
        cmnd = 'ietadm --op=new --tid=%d --user --params=IncomingUser=%s,Password=%s' % (tid, uname, passwd)

        process = subprocess.Popen(cmnd, stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            print 'IETADM error:'
            for line in process.stdout:
                print '\t', line,
            print 'Command was:', cmnd 

            return process.returncode 

        return 0

    def delete_target(self, tid):
        cmnd = 'ietadm --op=delete --tid=%d' % tid

        process = subprocess.Popen(cmnd, stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE, shell=True)

        process.wait()

        if process.returncode != 0:
            print 'IETADM error:'
            for line in process.stdout:
                print '\t', line,
            print 'Command was:', cmnd 

            return process.returncode 

        return 0

