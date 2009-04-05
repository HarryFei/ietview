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

import iet_target

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

    def add_lun(self, tid, lun, path, type, scsiid='', scsisn='', iomode=''):
        cmnd = 'ietadm --op=new --tid=%d --lun=%d --params=Path=%s,Type=%s' \
                % (tid, lun, path, type)

        if scsiid:
            cmnd = cmnd + ',ScsiId=%s' % scsiid

        if scsisn:
            cmnd = cmnd + ',ScsiSN=%s' % scsisn

        if iomode:
            cmnd = cmnd + ',IOMode=%s' % iomode

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
            uname, passwd = value.split('/')
            if tid > 0:
                cmnd = 'ietadm --op=new --tid=%d --user --params=OutgoingUser=%s,Password=%s' % (tid, uname, passwd)
            else:
                cmnd = 'ietadm --op=new --user --params=OutgoingUser=%s,Password=%s' % (uname, passwd)
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
        if tid > 0:
            cmnd = 'ietadm --op=new --tid=%d --user --params=IncomingUser=%s,Password=%s' % (tid, uname, passwd)
        else:
            cmnd = 'ietadm --op=new --user --params=IncomingUser=%s,Password=%s' % (uname, passwd)


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

    def delete_lun(self, tid, lun):
        cmnd = 'ietadm --op=delete --tid=%d --lun=%d' % (tid, lun)

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

    def delete_user(self, tid, uname):
        if tid > 0:
            cmnd = 'ietadm --op=delete --tid=%d --user --params=IncomingUser=%s' % (tid, uname)
        else:
            cmnd = 'ietadm --op=delete --user --params=IncomingUser=%s' % uname


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

    def delete_option(self, tid, key, value):
        if key == 'OutgoingUser':
            uname, passwd = value.split('/')

            if tid > 0:
                cmnd = 'ietadm --op=delete --tid=%d --user --params=OutgoingUser=%s' % (tid, uname)
            else:
                cmnd = 'ietadm --op=delete --user --params=OutgoingUser=%s' %  uname
        else:
            # TODO: throw expception
            pass

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

    def delete_connection(self, tid, sid, cid):
        cmnd = 'ietadm --op=delete --tid=%d --sid=%d --cid=%d' \
                % (tid, sid, cid)

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

    def update(self, target, diff):
        for op, type, val in diff:
            if type == 'option':
                key, val = val.split('=')

                if op == iet_target.IetTarget.ADD:
                    self.add_option(target.tid, key, val)
                elif op == iet_target.IetTarget.UPDATE:
                    self.add_option(target.tid, key, val)
                elif op == iet_target.IetTarget.DELETE:
                    self.delete_option(target.tid, key, val)
            elif type == 'lun':
                if op == iet_target.IetTarget.ADD:
                    self.add_lun(target.tid, val.number, val.path, val.iotype, **val.options)
                elif op == iet_target.IetTarget.DELETE:
                    self.delete_lun(target.tid, val.number)
                elif op == iet_target.IetTarget.UPDATE:
                    self.delete_lun(target.tid, val.number)
                    self.add_lun(target.tid, val.number, val.path, val.iotype, **val.options)
            elif type == 'user':
                uname, passwd = val.split('/')

                if op == iet_target.IetTarget.ADD:
                    self.add_user(target.tid, uname, passwd)
                elif op == iet_target.IetTarget.DELETE:
                    self.delete_user(target.tid, uname)
                elif op == iet_target.IetTarget.UPDATE:
                    self.delete_user(target.tid, uname)
                    self.add_user(target.tid, uname, passwd)


