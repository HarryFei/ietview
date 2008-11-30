#!/usr/bin/python

#  IETView is a GUI tool used to manage iSCSI targets
#  Copyright (C) 2008,2009 Jeffrey Panczyk <jpanczyk@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
import gtk
import gtk.glade
import pango
import iet_session
import iet_volume
import iet_allowdeny
import ietadm
import target_addedit

class IETView:
    def __init__(self):
        self.gladefile = 'IETView.glade'
        self.wTree = gtk.glade.XML(self.gladefile)

        self.main_window = self.wTree.get_widget('main_window')

        if self.main_window:
            self.main_window.connect('destroy', gtk.main_quit)

        self.target_store = gtk.TreeStore(str)

        self.reload_sessions()
        self.treeview = self.wTree.get_widget('session_tree')

        #self.treeview.connect('cursor-changed', self.cursor_changed)
        self.treeview.set_model(self.target_store)
        self.tvcolumn = gtk.TreeViewColumn('iSCSI Targets')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(-1)
        self.treeview.set_reorderable(False)

        self.textview = self.wTree.get_widget('session_view')
        self.add_button = self.wTree.get_widget('target_add')
        #self.add_button.connect('clicked', self.add_target)
        self.edit_button = self.wTree.get_widget('target_edit')
        self.edit_button.set_sensitive(False)
        #self.edit_button.connect('clicked', self.edit_target)
        self.delete_button = self.wTree.get_widget('target_delete')
        self.delete_button.set_sensitive(False)
        #self.delete_button.connect('clicked', self.delete_target)

        self.addedit_dialog = target_addedit.target_addedit(self.wTree)

        dic = { 'session_tree_cursor_changed_cb' : self.cursor_changed,
                'target_add_clicked_cb' : self.add_target,
                'target_edit_clicked_cb' : self.edit_target,
                'target_delete_clicked_cb' : self.delete_target,
                'lun_add_clicked_cb' : self.addedit_dialog.add_lun,
                'lun_edit_clicked_cb' : self.addedit_dialog.edit_lun,
                'lun_delete_clicked_cb' : self.addedit_dialog.delete_lun,
                'lun_browse_clicked_cb' : self.addedit_dialog.path_browse_lun

              }

        self.wTree.signal_autoconnect (dic)
        self.treeview.expand_row((0), False)

    def reload_sessions(self):
        self.target_store.clear()

        self.iets = iet_session.iet_sessions()
        self.iets.parse('/proc/net/iet/session')

        active_targets = self.target_store.append(None, ['Active Targets'])
        
        for session in self.iets.sessions:
            piter = self.target_store.append(active_targets, [ session.name ])
            for client in session.session_list:
                self.target_store.append(piter, [ '%s/%s (%s)' % (client.ip, client.initiator, client.state)])

        disabled_targets = self.target_store.append(None, ['Disabled Targets'])

        self.ietv = iet_volume.target_volumes()
        self.ietv.parse('/proc/net/iet/volume') 

        self.iet_allow = iet_allowdeny.iet_allowdeny()
        self.iet_allow.parse('/etc/initiators.allow')

        self.iet_deny = iet_allowdeny.iet_allowdeny()
        self.iet_deny.parse('/etc/initiators.deny')

    def delete_target(self, button):
        path, col = self.treeview.get_cursor()
        if path == None: return
        if len(path) != 2: return

        x = path[1]

        delete_dialog = self.wTree.get_widget('target_delete_dialog')
        response = delete_dialog.run()

        if response:
            adm = ietadm.ietadm()
            adm.delete_target(self.iets.sessions[x].tid)

        delete_dialog.hide()

        self.reload_sessions()

    def add_target(self, button):
        response = self.addedit_dialog.run_add()

        if response == gtk.RESPONSE_NONE or response == 0: return

        tname = self.addedit_dialog.tname.get_text()
        print 'Operation:', 'Add'
        print 'Target Name:', tname
        tid = len(self.iets.sessions) + 1
        print 'Tid:', tid
        print 'Active:', ( 'No', 'Yes' )[self.addedit_dialog.active.get_active()]
        print 'Saved:', ( 'No', 'Yes' )[self.addedit_dialog.saved.get_active()]
        print 'Lun Info:'

        adm = ietadm.ietadm()
        adm.add_target(tid, tname)

        for idx, row in enumerate(self.addedit_dialog.lun_store):
            print idx, row[0], row[1]
            adm.add_lun(tid, lun=idx, path=row[0], type=row[1])

        self.reload_sessions()
 
    def edit_target(self, button):
        path, col = self.treeview.get_cursor()
        if path == None: return
        if len(path) != 2: return

        x = path[1]
        session = self.iets.sessions[x]
        target = self.ietv.volumes[session.tid]

        response = self.addedit_dialog.run_edit(target)

        if response == gtk.RESPONSE_NONE or response == 0: return

        tname = self.addedit_dialog.tname.get_text()
        print 'Operation:', 'Edit'
        print 'Target Name:', tname

        print 'Tid:', session.tid
        print 'Active:', ( 'No', 'Yes' )[self.addedit_dialog.active.get_active()]
        print 'Saved:', ( 'No', 'Yes' )[self.addedit_dialog.saved.get_active()]

#        if tname != target.name:
#            changes['Name'] = tname

        print 'Lun Info:'
        for idx, row in enumerate(self.addedit_dialog.lun_store):
            print idx, row[0], row[1]

#        adm = ietadm.ietadm()
#        adm.update_target(tid, changes)

#            adm.add_lun(tid, lun=idx, path=row[0], type=row[1])
#

        self.reload_sessions()


    def cursor_changed(self, treeview):
        path, col = treeview.get_cursor()
        
        if path == None: return
        if len(path) == 1: return

        if len(path) == 2:
            x = path[1]
            buf = gtk.TextBuffer()
            buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'TID: ', 'Bold')
            buf.insert(buf.get_end_iter(), str(self.iets.sessions[x].tid) + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'Name: ', 'Bold')
            buf.insert(buf.get_end_iter(), self.iets.sessions[x].name + '\n')

            tid = self.iets.sessions[x].tid
            target = self.ietv.volumes[tid]
            luns = target.luns.keys()
            luns.sort()
            for lk in luns:
                lun = target.luns[lk]

                buf.insert_with_tags_by_name(buf.get_end_iter(), 'LUN: ', 'Bold')
                buf.insert(buf.get_end_iter(), str(lun.lun) + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), '\tPath: ', 'Bold')
                buf.insert(buf.get_end_iter(), lun.path + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), '\tState: ', 'Bold')
                buf.insert(buf.get_end_iter(), str(lun.state) + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), '\tIO Type: ', 'Bold')
                buf.insert(buf.get_end_iter(), lun.iotype + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), '\tIO Mode: ', 'Bold')
                buf.insert(buf.get_end_iter(), lun.iomode + '\n')

            buf.insert_with_tags_by_name(buf.get_end_iter(), 'Deny: ', 'Bold')

            if self.iets.sessions[x].name in self.iet_deny.initiators:
                buf.insert(buf.get_end_iter(), str(self.iet_deny.initiators[self.iets.sessions[x].name]) + '\n')
            else:
                buf.insert(buf.get_end_iter(), '\n')

            buf.insert_with_tags_by_name(buf.get_end_iter(), 'Allow: ', 'Bold')

            if self.iets.sessions[x].name in self.iet_allow.initiators:
                buf.insert(buf.get_end_iter(), str(self.iet_allow.initiators[self.iets.sessions[x].name]) + '\n')
            else:
                buf.insert(buf.get_end_iter(), '\n')

            adm = ietadm.ietadm()
            params = {}
            adm.show(params, self.iets.sessions[x].tid)
            keys = params.keys()
            keys.sort()
            for key in keys:
                buf.insert_with_tags_by_name(buf.get_end_iter(), key, 'Bold')
                buf.insert(buf.get_end_iter(), ': %s\n' % params[key])

            self.textview.set_buffer(buf)

            self.delete_button.set_sensitive(True)
            self.edit_button.set_sensitive(True)
        else:
            x = path(1)
            y = path(2)
            x, y = int(x), int(y)
            client = self.iets.sessions[x].session_list[y]
            buf = gtk.TextBuffer()
            buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'SID: ', 'Bold')
            buf.insert(buf.get_end_iter(), str(client.sid) + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'Initiator Name: ', 'Bold')
            buf.insert(buf.get_end_iter(), client.initiator + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'CID: ', 'Bold')
            buf.insert(buf.get_end_iter(), str(client.cid) + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'IP: ', 'Bold')
            buf.insert(buf.get_end_iter(), client.ip + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'State: ', 'Bold')
            buf.insert(buf.get_end_iter(), client.state + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'HD: ', 'Bold')
            buf.insert(buf.get_end_iter(), client.hd + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 'DD: ', 'Bold')
            buf.insert(buf.get_end_iter(), client.dd + '\n')

            adm = ietadm.ietadm()
            params = {}
            adm.show(params, self.iets.sessions[x].tid, client.sid)
            keys = params.keys()
            keys.sort()
            for key in keys:
                buf.insert_with_tags_by_name(buf.get_end_iter(), key, 'Bold')
                buf.insert(buf.get_end_iter(), ': %s\n' % params[key])


            self.textview.set_buffer(buf)

            self.delete_button.set_sensitive(False)
            self.edit_button.set_sensitive(False)
        
if __name__ == '__main__':
    iet_view = IETView()
    gtk.main()
