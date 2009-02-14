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

import gtk
import ietadm

class TargetAddEdit(object):
    options = [
        'OutgoingUser',
        'Alias',
        'MaxConnections',
        'ImmediateData',
        'MaxRecvDataSegmentLength',
        'MaxXmitDataSegmentLength',
        'MaxBurstLength',
        'FirstBurstLength',
        'DefaultTime2Wait',
        'DefaultTime2Retain',
        'MaxOutstandingR2T',
        'DataPDUInOrder',
        'DataSequenceInOrder',
        'ErrorRecoveryLevel',
        'HeaderDigest',
        'DataDigest',
        'Wthreads' ]

    def __init__(self, widgets):
        self.wTree = widgets
        self.option_store = gtk.ListStore(str, str)
        self.lun_store = gtk.ListStore(str, str)
        self.user_store = gtk.ListStore(str, str)
        self.deny_store = gtk.ListStore(str)
        self.allow_store = gtk.ListStore(str)
        self.option_names = gtk.ListStore(str)

        self.tname = self.wTree.get_widget('addedit_tname')
        self.active = self.wTree.get_widget('addedit_active')
        self.saved = self.wTree.get_widget('addedit_saved')
        self.dialog = self.wTree.get_widget('target_addedit_dialog')

        # Set up LUN Table
        self.lun_list = self.wTree.get_widget('lun_list')
        self.lun_list.set_model(self.lun_store)
        lun_col = gtk.TreeViewColumn('Path')
        lun_cell = gtk.CellRendererText()
        lun_col.pack_start(lun_cell, True)
        lun_col.add_attribute(lun_cell, 'text', 0)
        lun_col.set_sort_column_id(-1)
        self.lun_list.append_column(lun_col)

        lun_col = gtk.TreeViewColumn('Type')
        lun_cell = gtk.CellRendererText()
        lun_col.pack_start(lun_cell, True)
        lun_col.add_attribute(lun_cell, 'text', 1)
        lun_col.set_sort_column_id(-1)
        self.lun_list.append_column(lun_col)

        self.lun_list.set_search_column(0)
        self.lun_list.set_reorderable(False)

        # Set up initiators.allow table
        self.allow_list = self.wTree.get_widget('allow_list')
        self.allow_list.set_model(self.allow_store)
        allow_col = gtk.TreeViewColumn('Host or Subnet')
        allow_cell = gtk.CellRendererText()
        allow_col.pack_start(allow_cell, True)
        allow_col.add_attribute(allow_cell, 'text', 0)
        allow_col.set_sort_column_id(-1)
        self.allow_list.append_column(allow_col)
        self.allow_list.set_search_column(0)
        self.allow_list.set_reorderable(False)
        self.allow_list.set_headers_visible(False)

        # Set up initiators.deny table
        self.deny_list = self.wTree.get_widget('deny_list')
        self.deny_list.set_model(self.deny_store)
        deny_col = gtk.TreeViewColumn('Host or Subnet')
        deny_cell = gtk.CellRendererText()
        deny_col.pack_start(deny_cell, True)
        deny_col.add_attribute(deny_cell, 'text', 0)
        deny_col.set_sort_column_id(-1)
        self.deny_list.append_column(deny_col)
        self.deny_list.set_search_column(0)
        self.deny_list.set_reorderable(False)
        self.deny_list.set_headers_visible(False)

        # Set up incoming users table
        self.user_list = self.wTree.get_widget('user_list')
        self.user_list.set_model(self.user_store)
        user_col = gtk.TreeViewColumn('Username')
        user_cell = gtk.CellRendererText()
        user_col.pack_start(user_cell, True)
        user_col.add_attribute(user_cell, 'text', 0)
        user_col.set_sort_column_id(-1)
        self.user_list.append_column(user_col)

        user_col = gtk.TreeViewColumn('Password')
        user_cell = gtk.CellRendererText()
        user_col.pack_start(user_cell, True)
        user_col.add_attribute(user_cell, 'text', 1)
        user_col.set_sort_column_id(-1)
        self.user_list.append_column(user_col)

        self.user_list.set_search_column(0)
        self.user_list.set_reorderable(False)

        # Set up options table
        self.option_list = self.wTree.get_widget('option_list')
        self.option_list.set_model(self.option_store)
        option_col = gtk.TreeViewColumn('Key')
        option_cell = gtk.CellRendererText()
        option_col.pack_start(option_cell, True)
        option_col.add_attribute(option_cell, 'text', 0)
        option_col.set_sort_column_id(-1)
        self.option_list.append_column(option_col)

        option_col = gtk.TreeViewColumn('Value')
        option_cell = gtk.CellRendererText()
        option_col.pack_start(option_cell, True)
        option_col.add_attribute(option_cell, 'text', 1)
        option_col.set_sort_column_id(-1)
        self.option_list.append_column(option_col)

        self.option_list.set_search_column(0)
        self.option_list.set_reorderable(False)

        # Set up options combobox
        option_name = self.wTree.get_widget('option_name')
        for option in self.options:
            #option_name.append_text(option)
            self.option_names.append([option])

        option_name.set_model(self.option_names)

        # Set up signal handlers
        deny_add = self.wTree.get_widget('deny_add')
        deny_add.connect('clicked', self.add_allowdeny, self.deny_list)

        deny_edit = self.wTree.get_widget('deny_edit')
        deny_edit.connect('clicked', self.edit_allowdeny, self.deny_list)

        deny_delete = self.wTree.get_widget('deny_delete')
        deny_delete.connect('clicked', self.delete_allowdeny, self.deny_list)

        allow_add = self.wTree.get_widget('allow_add')
        allow_add.connect('clicked', self.add_allowdeny, self.allow_list)

        allow_edit = self.wTree.get_widget('allow_edit')
        allow_edit.connect('clicked', self.edit_allowdeny, self.allow_list)

        allow_delete = self.wTree.get_widget('allow_delete')
        allow_delete.connect('clicked', self.delete_allowdeny, self.allow_list)

    def run_add(self):
        self.tname.set_text('')
        self.tname.grab_focus()
        self.active.set_active(True)
        self.saved.set_active(True)

        self.option_store.clear()
        self.lun_store.clear()
        self.user_store.clear()
        self.deny_store.clear()
        self.allow_store.clear()

        notebook = self.wTree.get_widget('target_addedit_notebook')
        notebook.set_current_page(0)

        response = self.dialog.run()

        self.dialog.hide()

        return response

    def run_edit(self, active, session, vol, allow, deny, conf):
        notebook = self.wTree.get_widget('target_addedit_notebook')
        notebook.set_current_page(0)

        self.active.set_active(active)
        self.saved.set_active(conf != None)

        #TODO: Have to compare config options with runtime options
        # from ietadm, and somehow display that.
        self.option_store.clear()
        if active:
            self.tname.set_text(vol.target)
            self.tname.set_sensitive(False)
            adm = ietadm.IetAdm()
            params = {}
            adm.show(params, session.tid, sid=0)
            for key in sorted(params.iterkeys()):
                self.option_store.append([key, params[key]])

            luns = vol.luns
        else:
            self.tname.set_text(conf.name)
            for key, val in conf.options.iteritems():
                self.option_store.append([key, val])

            luns = conf.luns
            
        self.lun_store.clear()
        for lun in luns.itervalues():
            self.lun_store.append([lun.path, lun.iotype])

        self.user_store.clear()

        if conf != None:
            for user, passwd in conf.users.iteritems():
                self.user_store.append([user, passwd])

        self.deny_store.clear()
        for host in deny:
            self.deny_store.append([host.strip()])

        self.allow_store.clear()
        for host in allow:
            self.allow_store.append([host.strip()])

        response = self.dialog.run()

        self.dialog.hide()

        self.tname.set_sensitive(True)
        return response

    def add_lun(self, button):
        lun_addedit = self.wTree.get_widget('lun_addedit_dialog')
        lun_path = self.wTree.get_widget('lun_path')
        lun_fileio = self.wTree.get_widget('lun_type_fileio')
        lun_blockio = self.wTree.get_widget('lun_type_blockio')

        lun_path.set_text('')
        lun_fileio.set_active(True)

        response = lun_addedit.run()
        lun_addedit.hide()

        if response == 1:
            if lun_fileio.get_active():
                type = 'fileio'
            else:
                type = 'blockio'

            self.lun_store.append([ lun_path.get_text(), type ])
        
    def edit_lun(self, button):
        path, col = self.lun_list.get_cursor()
        if path == None: return

        path = path[0]

        lun_addedit = self.wTree.get_widget('lun_addedit_dialog')
        lun_path = self.wTree.get_widget('lun_path')
        lun_fileio = self.wTree.get_widget('lun_type_fileio')
        lun_blockio = self.wTree.get_widget('lun_type_blockio')

        lun_path.set_text(self.lun_store[path][0])
        if self.lun_store[path][1] == 'fileio':
            lun_fileio.set_active(True)
        else:
            lun_blockio.set_active(True)

        response = lun_addedit.run()
        lun_addedit.hide()

        if response == 1:
            if lun_fileio.get_active():
                type = 'fileio'
            else:
                type = 'blockio'

            self.lun_store[path] = [ lun_path.get_text(), type ]
 

    def delete_lun(self, button):
        path, col = self.lun_list.get_cursor()
        if path == None:
            return

        path = path[0]
        del self.lun_store[path]

    def path_browse_lun(self, button):
        lun_path = self.wTree.get_widget('lun_path')
        lun_browse = self.wTree.get_widget('lun_browse_dialog')
        response = lun_browse.run()
        lun_browse.hide()

        if response == 1:
            lun_path.set_text(lun_browse.get_filename())

    def lun_dialog_ok(self, entry):
        lun_addedit = self.wTree.get_widget('lun_addedit_dialog')
        lun_addedit.response(1)

    def add_option(self, button):
        option_addedit = self.wTree.get_widget('option_addedit_dialog')
        option_name = self.wTree.get_widget('option_name')
        option_value = self.wTree.get_widget('option_value')
        option_password = self.wTree.get_widget('option_password')
        option_password_label = self.wTree.get_widget('option_password_label')

        option_name.set_active(-1)
        option_value.set_text('')
        option_password.set_text('')
        option_password.hide()
        option_password_label.hide()

        response = option_addedit.run()
        option_addedit.hide()

        if response == 1:
            #TODO: validate input
            if option_name.get_active_text() == 'OutgoingUser':
                self.option_store.append([ option_name.get_active_text(), '%s/%s' % (option_value.get_text(), option_password.get_text()) ])
            else:
                self.option_store.append([ option_name.get_active_text(), option_value.get_text() ])


    def edit_option(self, button):
        option_addedit = self.wTree.get_widget('option_addedit_dialog')
        option_name = self.wTree.get_widget('option_name')
        option_value = self.wTree.get_widget('option_value')
        option_password = self.wTree.get_widget('option_password')
        option_password_label = self.wTree.get_widget('option_password_label')

        path, col = self.option_list.get_cursor()
        if path == None:
            return

        key, value = self.option_store[path]

        option_name.set_active(self.options.index(key))

        if key == 'OutgoingUser':
            user, password = value.split('/')

            option_value.set_text(user)
            option_password.set_text(password)
            option_password.show()
            option_password_label.show()
        else:
            option_value.set_text(value)
            option_password.set_text('')
            option_password.hide()
            option_password_label.hide()

        option_value.grab_focus()

        response = option_addedit.run()
        option_addedit.hide()

        if response == 1:
            #TODO: validate input
            if option_name.get_active_text() == 'OutgoingUser':
                self.option_store[path] = [option_name.get_active_text(),
                                           '%s/%s' % (option_value.get_text(),
                                                    option_password.get_text())]
            else:
                self.option_store[path] = [option_name.get_active_text(),
                                           option_value.get_text()]

    def delete_option(self, button):
        path, col = self.option_list.get_cursor()
        if path == None:
            return

        key, value = self.option_store[path]

        msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                type = gtk.MESSAGE_QUESTION,
                                buttons = gtk.BUTTONS_YES_NO,
                                message_format = 'Delete this option?\n%s = %s'
                                                 % (key, value))

        response = msg.run()

        if response == gtk.RESPONSE_YES:
            del self.option_store[path]

        msg.destroy()

    def option_changed(self, combo):
        option_password = self.wTree.get_widget('option_password')
        option_value_label = self.wTree.get_widget('option_value_label')
        option_password_label = self.wTree.get_widget('option_password_label')

        if combo.get_active_text() == 'OutgoingUser':
            option_value_label.set_text('Username:')
            option_password.show()
            option_password_label.show()
        else:
            option_value_label.set_text('Value:')
            option_password.hide()
            option_password_label.hide()

    def add_user(self, button):
        user_addedit = self.wTree.get_widget('user_addedit_dialog')
        user_name = self.wTree.get_widget('user_name')
        user_password = self.wTree.get_widget('user_password')

        user_name.set_text('')
        user_name.grab_focus()
        user_password.set_text('')

        response = user_addedit.run()
        user_addedit.hide()

        if response == 1:
            #TODO: validate input
            self.user_store.append([user_name.get_text(),
                                    user_password.get_text()])

    def edit_user(self, button):
        user_addedit = self.wTree.get_widget('user_addedit_dialog')
        user_name = self.wTree.get_widget('user_name')
        user_password = self.wTree.get_widget('user_password')

        path, col = self.user_list.get_cursor()
        if path == None:
            return

        user, passwd = self.user_store[path]

        user_name.set_text(user)
        user_name.grab_focus()
        user_password.set_text(passwd)


        response = user_addedit.run()
        user_addedit.hide()

        if response == 1:
            #TODO: validate input
            self.user_store[path] = [user_name.get_text(),
                                     user_password.get_text()]

    def delete_user(self, button):
        path, col = self.user_list.get_cursor()
        if path == None:
            return

        user = self.user_store[path][0]

        msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                type = gtk.MESSAGE_QUESTION,
                                buttons = gtk.BUTTONS_YES_NO,
                                message_format = 'Delete this user?\n%s' % user)

        response = msg.run()

        if response == gtk.RESPONSE_YES:
            del self.user_store[path]

        msg.destroy()

    def add_allowdeny(self, button, view):
        allowdeny_addedit = self.wTree.get_widget('allowdeny_addedit_dialog')
        allowdeny_net = self.wTree.get_widget('allowdeny_net')
        allowdeny_mask = self.wTree.get_widget('allowdeny_mask')
        allowdeny_type = self.wTree.get_widget('allowdeny_type')

        allowdeny_type.set_active(-1)
        allowdeny_net.set_text('')
        allowdeny_net.set_sensitive(False)
        allowdeny_mask.set_text('')
        allowdeny_mask.set_sensitive(False)

        response = allowdeny_addedit.run()
        allowdeny_addedit.hide()

        if response == 1:
            store = view.get_model()

            #TODO: validate input
            if allowdeny_type.get_active() in [2, 3]:
                host = allowdeny_net.get_text()
                if host[0] != '[':
                    host = '[' + host

                if host[-1] != ']':
                    host = host + ']'

                allowdeny_net.set_text(host)

            if allowdeny_type.get_active() in [1, 3]:
                store.append(['%s/%s' % (allowdeny_net.get_text(), allowdeny_mask.get_text())])
            else:
                store.append([allowdeny_net.get_text()])

    def edit_allowdeny(self, button, view):
        allowdeny_addedit = self.wTree.get_widget('allowdeny_addedit_dialog')
        allowdeny_net = self.wTree.get_widget('allowdeny_net')
        allowdeny_mask = self.wTree.get_widget('allowdeny_mask')
        allowdeny_type = self.wTree.get_widget('allowdeny_type')

        path, col = view.get_cursor()
        if path == None:
            return

        store = view.get_model()

        entry = store[path][0]

        if entry == 'ALL':
            allowdeny_type.set_active(4)
        elif '/' in entry:
            net, mask = entry.split('/')

            if ':' in net:
                allowdeny_type.set_active(3)
            else:
                allowdeny_type.set_active(1)

            allowdeny_net.set_text(net)
            allowdeny_mask.set_text(mask)

        elif ':' in entry:
            allowdeny_type.set_active(2)
            allowdeny_net.set_text(entry)
        else:
            allowdeny_type.set_active(0)
            allowdeny_net.set_text(entry)

        self.allowdeny_type_changed(allowdeny_type)
        response = allowdeny_addedit.run()
        allowdeny_addedit.hide()

        if response == 1:
            if allowdeny_type.get_active() in [2,3]:
                host = allowdeny_net.get_text()
                if host[0] != '[':
                    host = '[' + host

                if host[-1] != ']':
                    host = host + ']'

                allowdeny_net.set_text(host)


            #TODO: validate input
            if allowdeny_type.get_active() in [1, 3]:
                store[path] = ['%s/%s' % (allowdeny_net.get_text(), allowdeny_mask.get_text())]
            else:
                store[path] = [allowdeny_net.get_text()]

    def delete_allowdeny(self, button, view):
        path, col = view.get_cursor()
        if path == None:
            return

        store = view.get_model()

        entry = store[path][0]

        msg = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format='Delete this entry?\n%s'%entry)

        response = msg.run()

        if response == gtk.RESPONSE_YES:
            del store[path]

        msg.destroy()

    def allowdeny_type_changed(self, combo):
        # 0) IPv4 Host
        # 1) IPv4 Subnet
        # 2) IPv6 Host
        # 3) IPv6 Subnet
        # 4) ALL
        allowdeny_net = self.wTree.get_widget('allowdeny_net')
        allowdeny_mask = self.wTree.get_widget('allowdeny_mask')

        if combo.get_active() == 4:
            allowdeny_net.set_text('ALL')
            allowdeny_net.set_sensitive(False)
            allowdeny_mask.set_text('')
            allowdeny_mask.set_sensitive(False)
        elif combo.get_active() in [0, 2]:
            allowdeny_net.set_sensitive(True)
            allowdeny_net.grab_focus()
            allowdeny_mask.set_text('')
            allowdeny_mask.set_sensitive(False)
        elif combo.get_active() in [1, 3]:
            allowdeny_net.set_sensitive(True)
            allowdeny_net.grab_focus()
            allowdeny_mask.set_sensitive(True)
        else:
            allowdeny_net.set_text('')
            allowdeny_net.set_sensitive(False)
            allowdeny_mask.set_text('')
            allowdeny_mask.set_sensitive(False)



