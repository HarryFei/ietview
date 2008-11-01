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
import iet_session

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
            piter = self.treestore.append(None, ['%d %s' % (session.tid, session.name)])
            for client in session.session_list:
                self.treestore.append(piter, ['%d %s %s %s' % (client.sid, client.initiator, client.ip, client.state)])

        self.treeview = self.wTree.get_widget('session_tree')

        self.treeview.connect('cursor-changed', self.cursor_changed)
        self.treeview.set_model(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn('iSCSI Targets')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(False)

        self.textview = self.wTree.get_widget('session_view')


    def cursor_changed(self, treeview):
        path, col = treeview.get_cursor()
        
        if path == None: return

        if len(path) == 1:
            x = path[0]
            buf = gtk.TextBuffer()
            buf.set_text("%d %s" % (self.iets.sessions[x].tid, self.iets.sessions[x].name))
            self.textview.set_buffer(buf)
        else:
            x, y = path
            x, y = int(x), int(y)
            buf = gtk.TextBuffer()
            buf.set_text("%d %s" % (self.iets.sessions[x].session_list[y].sid, self.iets.sessions[x].session_list[y].initiator))
            self.textview.set_buffer(buf)

        

if __name__ == '__main__':
    iet_view = IETView()
    gtk.main()
