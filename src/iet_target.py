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
import ietadm

class IetLun(object):
    OPTIONS_REGEX=',?\s*(?P<key>\w+)\s*=\s*(?P<val>[^ \t\n\r\f\v,]+)'

    def __init__(self, number, path, iotype, **kwargs):
        self.number = number
        self.iotype = iotype
        self.path = path
        self.options = {}

        for option in ['state', 'iomode', 'scsiid', 'scsisn']:
            if option in kwargs and kwargs[option]:
                self.options[option] = kwargs[option]

    def add_options(self, in_opts):
        if in_opts == None:
            return

        for m in re.finditer(self.OPTIONS_REGEX, in_opts):
            if m.group('key').lower() in \
               ['state', 'scsiid', 'scsisn', 'iomode'] \
               and m.group('val') != None:

                self.options[m.group('key').lower()] = m.group('val')

    def write(self, f, prepend=''):
        f.write('%s\tLun %d Path=%s,Type=%s'
                % (prepend, self.number, self.path, self.iotype))

        for option in ['ScsiId', 'ScsiSN', 'IOMode']:
            if option.lower() in self.options:
                f.write(',%s=%s'%(option, self.options[option.lower()]))

        f.write('\n')

    def dump(self):
        print self.number, self.path, self.iotype

    def __eq__(self, other):
        if self.path != other.path or self.iotype != other.iotype:
            return False

        # Hacks to work around that active targets have an implicit iomode
        if 'iomode' in self.options:
            if self.options['iomode'] != 'wt' \
               and ('iomode' not in other.options 
                    or self.options['iomode'] != other.options['iomode']):

                return False

        if 'iomode' in other.options and other.options['iomode'] != 'wt':
            return False

        for key, val in self.options.iteritems():
            if key == 'iomode':
                continue
            if key not in other.options:
                return False
            elif val != other.options[key]:
                return False

        for key in other.options:
            if key == 'iomode':
                continue
            if key not in self.options:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class IetTarget(object):
    ADD = 0
    DELETE = 1
    UPDATE = 2

    def __init__(self, **kwargs):
        self.tid = 0
        self.name = ''

        self.luns = None
        self.allow = None
        self.deny = None

        self.users = None
        self.options = None

        self.active = False
        self.saved = False

        # Target's can also be initialized from the target add/edit dialog
        if 'dialog' in kwargs:
            return self.init_from_dialog(kwargs['dialog'])

        if kwargs['active']:
            return self.init_active(**kwargs)
        else:
            return self.init_inactive(**kwargs)

    def init_active(self, **kwargs):
        self.active = True
        self.tid = kwargs['session'].tid
        self.saved = kwargs['saved']
        self.name = kwargs['tname']
        self.luns = kwargs['vol'].luns
        self.allow = kwargs['allow']
        self.deny = kwargs['deny']

        # TODO: Can be reteived via ietadm with version 0.4.17
        if 'conf' in kwargs and kwargs['conf'] != None:
            self.users = kwargs['conf'].users

            for lun in self.luns.itervalues():
                if lun.number in kwargs['conf'].luns:
                    conf_lun = kwargs['conf'].luns[lun.number]
                    for option in ['scsiid', 'scsisn']:
                        if option in conf_lun.options:
                            lun.options[option] = conf_lun.options[option]

        else:
            self.users = {}

        self.options = {} 
        adm = ietadm.IetAdm()
        adm.show(self.options, kwargs['session'].tid, sid=0)
 
    def init_inactive(self, **kwargs):
        self.active = False
        self.saved = kwargs['saved']
        self.name = kwargs['tname']
        self.luns = kwargs['conf'].luns
        self.allow = kwargs['allow']
        self.deny = kwargs['deny']
        self.users = kwargs['conf'].users
        self.options = kwargs['conf'].options

    def init_from_dialog(self, dialog):
        self.active = dialog.active.get_active()
        self.saved = dialog.saved.get_active()
        self.name = dialog.tname.get_text()
        self.luns = {}
        i = 0
        for path, iotype, sid, ssn, mode in dialog.lun_store:
            self.luns[i] = IetLun(i, path, iotype, scsiid=sid, scsisn=ssn, iomode=mode)
            i += 1

        self.allow = []
        for row in dialog.allow_store:
            self.allow.append(row[0])

        self.deny = []
        for row in dialog.deny_store:
            self.deny.append(row[0])

        self.users = {}
        for uname, passwd in dialog.user_store:
            self.users[uname] = passwd

        self.options = {}
        for key, val in dialog.option_store:
            self.options[key] = val

    def diff(self, left = None, right = None):
        """ Return a set of instructions that updates the running config
            from this class to another """
        instructions = []

        if left == None and right == None:
            return []

        if left == None:
            left = self
        elif right == None:
            right = self

        if right.tid != left.tid:
            pass

        if left.active == False and right.active == True:
            instructions.append((self.UPDATE, 'active', True))
        elif left.active == True and right.active == False:
            instructions.append((self.UPDATE, 'active', False))

        if left.saved == False and right.saved == True:
            instructions.append((self.UPDATE, 'saved', True))
        elif left.saved == True and right.saved == False:
            instructions.append((self.UPDATE, 'saved', False))

        if right.name != left.name:
            instructions.append((self.UPDATE, 'name', right.name))

        for lun in left.luns.itervalues():
            if lun.number not in right.luns:
                instructions.append((self.DELETE, 'lun', lun))
            elif lun != right.luns[lun.number]:
                instructions.append((self.UPDATE, 'lun', right.luns[lun.number]))

        for lun in right.luns.itervalues():
            if lun.number not in left.luns:
                instructions.append((self.ADD, 'lun', lun))

        for allow in left.allow:
            if allow not in right.allow:
                instructions.append((self.DELETE, 'allow', allow))

        for allow in right.allow:
            if allow not in left.allow:
                instructions.append((self.ADD, 'allow', allow))

        for deny in left.deny:
            if deny not in right.deny:
                instructions.append((self.DELETE, 'deny', deny))

        for deny in right.deny:
            if deny not in left.deny:
                instructions.append((self.ADD, 'deny', deny))

        for key, val in left.options.iteritems():
            if key not in right.options:
                instructions.append((self.DELETE, 'option', '%s=%s' % (key, val)))
            elif val != right.options[key]:
                instructions.append((self.UPDATE, 'option', '%s=%s' % (key, right.options[key])))

        for key, val in right.options.iteritems():
            if key not in left.options:
                instructions.append((self.ADD, 'option', '%s=%s' % (key, val)))

        for uname, passwd in left.users.iteritems():
            if uname not in right.users:
                instructions.append((self.DELETE, 'user', '%s/%s' % (uname, passwd)))
            elif passwd != right.users[uname]:
                instructions.append((self.UPDATE, 'user', '%s/%s' % (uname, passwd)))

        for uname, passwd in right.users.iteritems():
            if uname not in left.users:
                instructions.append((self.ADD, 'user', '%s/%s' % (uname, passwd)))

        return instructions

    def dump(self):
        print 'Target Name:', self.name
        
        print 'LUNs:'
        for key in sorted(self.luns.keys()):
            print '\t',
            self.luns[key].dump()

        print 'Deny:', 
        for host in self.deny:
            print host,
        print

        print 'Allow:', 
        for host in self.allow:
            print host,
        print

        print 'Users:'
        for uname, passwd in self.users.iteritems():
            print '\t', uname, passwd

        print 'Options:'
        for key, val in self.options.iteritems():
            print '\t', key, val
