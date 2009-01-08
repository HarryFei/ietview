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
import iet_target
import iet_conf
import ietadm
import target_addedit

class IetView(object):
    def __init__(self):
        self.gladefile = 'IETView.glade'
        self.wTree = gtk.glade.XML(self.gladefile)

        self.main_window = self.wTree.get_widget('main_window')

        if self.main_window:
            self.main_window.connect('destroy', gtk.main_quit)

        self.target_store = gtk.TreeStore(str, str)

        self.target_list = self.wTree.get_widget('session_tree')
        self.target_list.set_model(self.target_store)
        self.tvcolumn = gtk.TreeViewColumn('iSCSI Targets')
        self.target_list.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.target_list.set_search_column(0)
        self.tvcolumn.set_sort_column_id(-1)
        self.target_list.set_reorderable(False)

        self.target_details = self.wTree.get_widget('session_view')
        self.add_button = self.wTree.get_widget('target_add')
        self.edit_button = self.wTree.get_widget('target_edit')
        self.edit_button.set_sensitive(False)
        self.delete_button = self.wTree.get_widget('target_delete')
        self.delete_button.set_sensitive(False)

        self.addedit_dialog = target_addedit.TargetAddEdit(self.wTree)

        dic = { 'session_tree_cursor_changed_cb' : self.cursor_changed,
                'target_add_clicked_cb' : self.add_target,
                'target_edit_clicked_cb' : self.edit_target,
                'target_delete_clicked_cb' : self.delete_target,
                'lun_add_clicked_cb' : self.addedit_dialog.add_lun,
                'lun_edit_clicked_cb' : self.addedit_dialog.edit_lun,
                'lun_delete_clicked_cb' : self.addedit_dialog.delete_lun,
                'lun_browse_clicked_cb' : self.addedit_dialog.path_browse_lun,
                'option_add_clicked_cb' : self.addedit_dialog.add_option,
                'option_edit_clicked_cb' : self.addedit_dialog.edit_option,
                'option_delete_clicked_cb' : self.addedit_dialog.delete_option,
                'user_add_clicked_cb' : self.addedit_dialog.add_user,
                'user_edit_clicked_cb' : self.addedit_dialog.edit_user,
                'user_delete_clicked_cb' : self.addedit_dialog.delete_user,
                'option_name_changed_cb' : self.addedit_dialog.option_changed,
                'allowdeny_type_changed_cb' : self.addedit_dialog.allowdeny_type_changed
              }

        self.wTree.signal_autoconnect (dic)

        self.reload_sessions()

    def reload_sessions(self):
        self.target_store.clear()

        self.iets = iet_session.IetSessions()
        self.iets.parse('/proc/net/iet/session')

        self.ietc = iet_conf.IetConfFile()
        self.ietc.parse('/etc/ietd.conf')

        active_targets = self.target_store.append(None, ['Active Targets', ''])
        
        for session in self.iets.sessions.itervalues():
            piter = self.target_store.append(active_targets, [ session.target, '' ])
            for client in session.clients.itervalues():
                self.target_store.append(piter,
                           [ '%s/%s (%s)' % (client.ip, client.initiator, client.state), client.initiator ])

        disabled_targets = self.target_store.append(None, ['Disabled Targets', ''])

        for target in self.ietc.inactive_targets.itervalues():
            self.target_store.append(disabled_targets, [ target.name, '' ])

        self.ietv = iet_volume.IetVolumes()
        self.ietv.parse('/proc/net/iet/volume') 

        self.iet_allow = iet_allowdeny.IetAllowDeny()
        self.iet_allow.parse('/etc/initiators.allow')

        self.iet_deny = iet_allowdeny.IetAllowDeny()
        self.iet_deny.parse('/etc/initiators.deny')

        self.target_list.expand_row((0), False)

    def delete_target(self, button):
        path, col = self.target_list.get_cursor()
        if path == None: return
        if len(path) != 2: return

        tname = self.target_store[path][0]

        msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                type = gtk.MESSAGE_QUESTION,
                                buttons = gtk.BUTTONS_YES_NO,
                                message_format = 
                                  'Permanently delete this target?\n%s' % tname)

        response = msg.run()

        if response == gtk.RESPONSE_YES:
            if path[0] == 0:
                adm = ietadm.IetAdm()
                adm.delete_target(self.iets.sessions[tname].tid)

            if tname in self.ietc.targets:
                del self.ietc.targets[tname]
                self.ietc.write('/etc/ietd.conf')

            if tname in self.ietc.inactive_targets:
                del self.ietc.inactive_targets[tname]
                self.ietc.write('/etc/ietd.conf')

            if tname in self.iet_deny.targets:
                del self.iet_deny.targets[tname]
                self.iet_deny.write('/etc/initiators.deny')

            if tname in self.iet_allow.targets:
                del self.iet_allow.targets[tname]
                self.iet_allow.write('/etc/initiators.allow')

            self.reload_sessions()
            self.target_details.set_buffer(gtk.TextBuffer())

        msg.destroy()

    def add_target(self, button):
        response = self.addedit_dialog.run_add()

        if response != 1:
            return

        tname = self.addedit_dialog.tname.get_text()
        print 'Operation:', 'Add'
        print 'Target Name:', tname

        # TODO: Add find lowest TID and LUNID functions 
        tid = len(self.iets.sessions) + 1
        print 'Tid:', tid

        active = self.addedit_dialog.active.get_active()
        print 'Active:', ( 'No', 'Yes' )[active]
        saved = self.addedit_dialog.saved.get_active()
        print 'Saved:', ( 'No', 'Yes' )[saved]

        if saved:
            self.ietc.add_target(tname, active, **dict(self.addedit_dialog.option_store))
            # TODO: replace with a get in IetConfFile
            if active:
                conf_target = self.ietc.targets[tname]
            else:
                conf_target = self.ietc.inactive_targets[tname]

            idx = 0
            for path, iotype in self.addedit_dialog.lun_store:
                conf_target.add_lun(idx, path, iotype)
                idx += 1

            for user, password in self.addedit_dialog.user_store:
                conf_target.add_user(user, password)

            for host in self.addedit_dialog.deny_store:
                self.iet_deny.add_host(tname, host[0])
    
            self.iet_deny.write('/etc/initiators.deny')
    
            for host in self.addedit_dialog.allow_store:
                self.iet_allow.add_host(tname, host[0])
    
            self.iet_allow.write('/etc/initiators.allow')

            self.ietc.write('/etc/ietd.conf')

        if active:
            adm = ietadm.IetAdm()
            adm.add_target(tid, tname)
    
            print 'Options:'
            for key, value in self.addedit_dialog.option_store:
                print '\t %s = %s' % (key, value)
                adm.add_option(tid, key, value)
    
            print 'Lun Info:'
            idx = 0
            for path, iotype in self.addedit_dialog.lun_store:
                print '\t', path, iotype
                adm.add_lun(tid, lun=idx, path=path, type=iotype)
                idx += 1
    
            print 'Incoming Users:'
            for user, password in self.addedit_dialog.user_store:
                print '\t', user, password
                adm.add_user(tid, user, password)
    
            print 'Hosts Deny:'
            for host in self.addedit_dialog.deny_store:
                print '\t', host[0]
                self.iet_deny.add_host(tname, host[0])
    
            self.iet_deny.write('/etc/initiators.deny')
    
            print 'Hosts Allow:'
            for host in self.addedit_dialog.allow_store:
                print '\t', host[0]
                self.iet_allow.add_host(tname, host[0])
    
            self.iet_allow.write('/etc/initiators.allow')
    
        self.reload_sessions()
     
    def edit_target(self, button):
        path, col = self.target_list.get_cursor()
        if path == None: return
        if len(path) != 2: return

        target = self.target_store[path][0]
        session = self.iets.sessions[target]
        vol = self.ietv.volumes[session.tid]
        allow = self.iet_allow.targets[target]
        deny = self.iet_deny.targets[target]
        conf = self.ietc.targets[target]

        response = self.addedit_dialog.run_edit(vol=vol,
                allow=allow, deny=deny, conf=conf)

        if response != 1:
            return

        old = iet_target.IetTarget(vol=vol, allow=allow, deny=deny) 

        new_target = iet_target.IetTarget(dialog=self.addedit_dialog)
        new_target.set_from_dialog()

        diff = old.diff(right=new)

        ietadm.update(old, diff)

        allow.update(old, diff)
        deny.update(old, diff)

        if self.addedit_dialog.saved.get_active():
            config.update(old, diff)

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

    def show_session_details(self, path):
        target = self.target_store[path][0]
        tid = self.iets.sessions[target].tid

        buf = gtk.TextBuffer()
        buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)
        buf.insert_with_tags_by_name(buf.get_end_iter(), 'TID: ', 'Bold')
        buf.insert(buf.get_end_iter(), str(tid) + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Name: ', 'Bold')
        buf.insert(buf.get_end_iter(), target + '\n')

        vol = self.ietv.volumes[tid]
        for lk in sorted(vol.luns.iterkeys()):
            lun = vol.luns[lk]

            buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                         'LUN: ', 'Bold')

            buf.insert(buf.get_end_iter(), str(lun.lun) + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(),
                                         '\tPath: ', 'Bold')
            
            buf.insert(buf.get_end_iter(), lun.path + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(),
                                         '\tState: ', 'Bold')

            buf.insert(buf.get_end_iter(), str(lun.state) + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                         '\tIO Type: ', 'Bold')

            buf.insert(buf.get_end_iter(), lun.iotype + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                         '\tIO Mode: ', 'Bold')

            buf.insert(buf.get_end_iter(), lun.iomode + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Deny: ', 'Bold')

        if target in self.iet_deny.targets:
            buf.insert(buf.get_end_iter(),
                       str(self.iet_deny.targets[target]) + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Allow: ', 'Bold')

        if target in self.iet_allow.targets:
            buf.insert(buf.get_end_iter(),
                       str(self.iet_allow.targets[target]) + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        adm = ietadm.IetAdm()
        params = {}
        adm.show(params, tid, sid=0)
        for key in sorted(params.iterkeys()):
            buf.insert_with_tags_by_name(buf.get_end_iter(), key, 'Bold')
            buf.insert(buf.get_end_iter(), ': %s\n' % params[key])

        self.target_details.set_buffer(buf)

    def show_client_details(self, path):
        target = self.target_store[path[0:2]][0]
        initiator = self.target_store[path][1]
        client = self.iets.sessions[target].clients[initiator]
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

        adm = ietadm.IetAdm()
        params = {}
        adm.show(params, self.iets.sessions[target].tid, client.sid)
        keys = params.keys()
        keys.sort()
        for key in keys:
            buf.insert_with_tags_by_name(buf.get_end_iter(), key, 'Bold')
            buf.insert(buf.get_end_iter(), ': %s\n' % params[key])


        self.target_details.set_buffer(buf)

    def show_config_details(self, path):
        tname = self.target_store[path][0]
        target = self.ietc.inactive_targets[tname]

        buf = gtk.TextBuffer()
        buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Name: ', 'Bold')
        buf.insert(buf.get_end_iter(), tname + '\n')

        for lk in sorted(target.luns.iterkeys()):
            lun = target.luns[lk]

            buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                         'LUN: ', 'Bold')

            buf.insert(buf.get_end_iter(), str(lun.number) + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(),
                                         '\tPath: ', 'Bold')
            
            buf.insert(buf.get_end_iter(), lun.path + '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                         '\tIO Type: ', 'Bold')

            buf.insert(buf.get_end_iter(), lun.type + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Deny: ', 'Bold')

        if tname in self.iet_deny.targets:
            buf.insert(buf.get_end_iter(),
                       str(self.iet_deny.targets[tname]) + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Allow: ', 'Bold')

        if tname in self.iet_allow.targets:
            buf.insert(buf.get_end_iter(),
                       str(self.iet_allow.targets[tname]) + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        for key, value in target.options:
            buf.insert_with_tags_by_name(buf.get_end_iter(), key, 'Bold')
            if type(value) == str:
                buf.insert(buf.get_end_iter(), ': %s\n' % value)
            else:
                buf.insert(buf.get_end_iter(), ': %s/%s\n' % value)

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Incoming Users:\n', 'Bold')
        for uname, passwd in target.users.iteritems():
            buf.insert(buf.get_end_iter(), '\t%s/%s\n' % (uname, passwd))

        self.target_details.set_buffer(buf)

    def cursor_changed(self, target_list):
        path, col = target_list.get_cursor()
        
        if path == None or len(path) == 1:
            return

        if len(path) == 2:
            if path[0] == 0:
                self.show_session_details(path)
            elif path[0] == 1:
                self.show_config_details(path)

            self.delete_button.set_sensitive(True)
            self.edit_button.set_sensitive(True)
        else:
            self.show_client_details(path)
            self.delete_button.set_sensitive(False)
            self.edit_button.set_sensitive(False)
        
if __name__ == '__main__':
    iet_view = IetView()
    gtk.main()
