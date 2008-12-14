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

class IetTarget(object):
    ADD = 0
    DELETE = 1
    UPDATE = 2

    def __init__(self, **kwargs):
        self.tid = tid
        self.name = name

        self.luns = None
        self.sessions = None
        self.allow = None
        self.deny = None

        self.options = None

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

        if right.name != left.name:
            instructions.append((self.UPDATE, "name", right.name))

        for lun in left.luns.itervalues():
            if lun.lun not in right.luns:
                instructions.append((self.DELETE, "lun", lun))
            elif lun != right.luns[lun.lun]:
                    instructions.append((self.DELETE, "lun", lun))
                    instructions.append((self.ADD, "lun", right.luns[lun.lun]))

        for lun in right.luns.itervalues():
            if lun.lun not in left.luns:
                instructions.append((self.ADD, "lun", lun))

        for allow in left.allow:
            if allow.host not in right.allow:
                instructions.append((self.DELETE, "allow", allow))

        for allow in right.allow:
            if allow.host not in left.allow:
                instructions.append((self.ADD, "allow", allow))

        for deny in left.deny:
            if deny.host not in right.deny:
                instructions.append((self.DELETE, "deny", deny))

        for deny in right.deny:
            if deny.host not in left.deny:
                instructions.append((self.ADD, "deny", deny))

        for key, val in left.options.iteritems():
            if key not in right.options:
                instructions.append((self.DELETE, "option", "%s=%s" % (key, value)))
            elif val != right.options[key]:
                instructions.append((self.UPDATE, "options", "%s=%s" % (key, value)))

        for key, val in right.options.iteritems():
            if key not in left.options:
                instructions.append((self.ADD, "option", "%s=%s" % (key, value)))

        return instructions

    def write(self):
        """ Write this target to a file in ietd.conf notation """
        pass

