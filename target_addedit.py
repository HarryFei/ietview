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

class TargetAddEdit(object):
    def __init__(self, widgets):
        self.wTree = widgets
        self.option_store = gtk.ListStore(str, str)
        self.lun_store = gtk.ListStore(str, str)
        self.user_store = gtk.ListStore(str, str)
        self.deny_store = gtk.ListStore(str)
        self.allow_store = gtk.ListStore(str)

        self.tname = self.wTree.get_widget('addedit_tname')
        self.active = self.wTree.get_widget('addedit_active')
        self.saved = self.wTree.get_widget('addedit_saved')
        self.dialog = self.wTree.get_widget('target_addedit_dialog')

        # Set up LUN Table
        self.lun_view = self.wTree.get_widget('lun_list')
        self.lun_view.set_model(self.lun_store)
        lun_col = gtk.TreeViewColumn('Path')
        lun_cell = gtk.CellRendererText()
        lun_col.pack_start(lun_cell, True)
        lun_col.add_attribute(lun_cell, 'text', 0)
        lun_col.set_sort_column_id(-1)
        self.lun_view.append_column(lun_col)

        lun_col = gtk.TreeViewColumn('Type')
        lun_cell = gtk.CellRendererText()
        lun_col.pack_start(lun_cell, True)
        lun_col.add_attribute(lun_cell, 'text', 1)
        lun_col.set_sort_column_id(-1)
        self.lun_view.append_column(lun_col)

        self.lun_view.set_search_column(0)
        self.lun_view.set_reorderable(False)

        # Set up initiators.allow table
        self.allow_view = self.wTree.get_widget('allow_list')
        self.allow_view.set_model(self.allow_store)
        allow_col = gtk.TreeViewColumn('Host or Subnet')
        allow_cell = gtk.CellRendererText()
        allow_col.pack_start(allow_cell, True)
        allow_col.add_attribute(allow_cell, 'text', 0)
        allow_col.set_sort_column_id(-1)
        self.allow_view.append_column(allow_col)
        self.allow_view.set_search_column(0)
        self.allow_view.set_reorderable(False)
        self.allow_view.set_headers_visible(False)

        # Set up initiators.deny table
        self.deny_view = self.wTree.get_widget('deny_list')
        self.deny_view.set_model(self.deny_store)
        deny_col = gtk.TreeViewColumn('Host or Subnet')
        deny_cell = gtk.CellRendererText()
        deny_col.pack_start(deny_cell, True)
        deny_col.add_attribute(deny_cell, 'text', 0)
        deny_col.set_sort_column_id(-1)
        self.deny_view.append_column(deny_col)
        self.deny_view.set_search_column(0)
        self.deny_view.set_reorderable(False)
        self.deny_view.set_headers_visible(False)

        # Set up incoming users table
        self.user_view = self.wTree.get_widget('user_list')
        self.user_view.set_model(self.user_store)
        user_col = gtk.TreeViewColumn('Username')
        user_cell = gtk.CellRendererText()
        user_col.pack_start(user_cell, True)
        user_col.add_attribute(user_cell, 'text', 0)
        user_col.set_sort_column_id(-1)
        self.user_view.append_column(user_col)

        user_col = gtk.TreeViewColumn('Password')
        user_cell = gtk.CellRendererText()
        user_col.pack_start(user_cell, True)
        user_col.add_attribute(user_cell, 'text', 1)
        user_col.set_sort_column_id(-1)
        self.user_view.append_column(user_col)

        self.user_view.set_search_column(0)
        self.user_view.set_reorderable(False)

    def run_add(self):
        self.tname.set_text('')
        self.active.set_active(True)
        self.saved.set_active(True)

        self.option_store.clear()
        self.lun_store.clear()
        self.user_store.clear()
        self.deny_store.clear()
        self.allow_store.clear()

        response = self.dialog.run()

        self.dialog.hide()

        return response

    def run_edit(self, vol, allow, deny, conf):
        self.tname.set_text(vol.target)
        #TODO: Allow editing of inactive targets

        self.active.set_active(True)
        self.saved.set_active(True)

        self.option_store.clear()
        self.lun_store.clear()

        for lun in vol.luns.itervalues():
            self.lun_store.append([lun.path, lun.iotype])

        self.user_store.clear()
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
        path, col = self.lun_view.get_cursor()
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
        path, col = self.lun_view.get_cursor()
        if path == None: return

        path = path[0]
        del self.lun_store[path]

    def path_browse_lun(self, button):
        lun_path = self.wTree.get_widget('lun_path')
        lun_browse = self.wTree.get_widget('lun_browse_dialog')
        response = lun_browse.run()
        lun_browse.hide()

        if response == 1: lun_path.set_text(lun_browse.get_filename())




