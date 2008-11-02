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

class IETView:
    def __init__(self):
        self.gladefile = 'IETView.glade'
        self.wTree = gtk.glade.XML(self.gladefile)

        self.main_window = self.wTree.get_widget('main_window')

        if self.main_window:
            self.main_window.connect('destroy', gtk.main_quit)

        self.treestore = gtk.TreeStore(str)

        self.iets = iet_session.iet_sessions()
        self.iets.parse('/home/jpanczyk/proc_session')
        
        for session in self.iets.sessions:
            piter = self.treestore.append(None, [ session.name ])
            for client in session.session_list:
                self.treestore.append(piter, [ '%s/%s (%s)' % (client.ip, client.initiator, client.state)])

        self.ietv = iet_volume.target_volumes()
        self.ietv.parse('/home/jpanczyk/proc_volume') 

        self.iet_allow = iet_allowdeny.iet_allowdeny()
        self.iet_allow.parse('/home/jpanczyk/iet_allow')

        self.iet_deny = iet_allowdeny.iet_allowdeny()
        self.iet_deny.parse('/home/jpanczyk/iet_deny')

        self.treeview = self.wTree.get_widget('session_tree')

        self.treeview.connect('cursor-changed', self.cursor_changed)
        self.treeview.set_model(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn('iSCSI Targets')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(-1)
        self.treeview.set_reorderable(False)

        self.textview = self.wTree.get_widget('session_view')


    def cursor_changed(self, treeview):
        path, col = treeview.get_cursor()
        
        if path == None: return

        if len(path) == 1:
            x = path[0]
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
                buf.insert_with_tags_by_name(buf.get_end_iter(), 'Path: ', 'Bold')
                buf.insert(buf.get_end_iter(), lun.path + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), 'State: ', 'Bold')
                buf.insert(buf.get_end_iter(), str(lun.state) + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), 'IO Type: ', 'Bold')
                buf.insert(buf.get_end_iter(), lun.iotype + '\n')
                buf.insert_with_tags_by_name(buf.get_end_iter(), 'IO Mode: ', 'Bold')
                buf.insert(buf.get_end_iter(), lun.iomode + '\n')

            buf.insert_with_tags_by_name(buf.get_end_iter(), 'Allow: ', 'Bold')

            if self.iets.sessions[x].name in self.iet_allow.initiators:
                buf.insert(buf.get_end_iter(), str(self.iet_allow.initiators[self.iets.sessions[x].name]) + '\n')
            else:
                buf.insert(buf.get_end_iter(), '\n')

            buf.insert_with_tags_by_name(buf.get_end_iter(), 'Deny: ', 'Bold')

            if self.iets.sessions[x].name in self.iet_deny.initiators:
                buf.insert(buf.get_end_iter(), str(self.iet_deny.initiators[self.iets.sessions[x].name]) + '\n')
            else:
                buf.insert(buf.get_end_iter(), '\n')
            
            self.textview.set_buffer(buf)
        else:
            x, y = path
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
            self.textview.set_buffer(buf)

        
if __name__ == '__main__':
    iet_view = IETView()
    gtk.main()
