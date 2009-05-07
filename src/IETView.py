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

import os
import sys
import shutil
import filecmp

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
    CONF_FILE_PATH = '/etc/ietd.conf'
    INITIATORS_ALLOW_PATH = '/etc/initiators.allow'
    INITIATORS_DENY_PATH = '/etc/initiators.deny'
    SESSION_PATH = '/proc/net/iet/session'
    VOLUME_PATH = '/proc/net/iet/volume'
    GLADE_FILE_PATH = '/usr/share/IETView/IETView.glade'

    def __init__(self):
        if os.path.exists('src/IETView.glade'):
            self.gladefile = 'src/IETView.glade'
        elif os.path.exists(self.GLADE_FILE_PATH):
            self.gladefile = self.GLADE_FILE_PATH
        else:
            print 'Could not find critial resource file IETView.glade.\n' \
                  'Is IETView installed correctly?'

            sys.exit(1)

        self.wTree = gtk.glade.XML(self.gladefile)
        self.main_window = self.wTree.get_widget('main_window')

        if self.main_window:
            self.main_window.connect('destroy', gtk.main_quit)

        accel_group = gtk.AccelGroup()
        self.main_window.add_accel_group(accel_group)
        refresh = self.wTree.get_widget('refresh_menu_item')
        refresh.add_accelerator('activate', accel_group, 
                gtk.gdk.keyval_from_name('F5'),
                0, gtk.ACCEL_VISIBLE)

        
        self.target_store = gtk.TreeStore(str, str, str, str, str)

        self.target_list = self.wTree.get_widget('session_tree')
        self.target_list.set_model(self.target_store)
        self.tvcolumn = gtk.TreeViewColumn('iSCSI Targets')
        self.target_list.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.target_list.set_search_column(0)
        self.tvcolumn.set_sort_column_id(-1)
        self.tvcolumn.set_cell_data_func(self.cell, self.bold_cell)
        self.target_list.set_reorderable(False)

        self.target_details = self.wTree.get_widget('session_view')
        margin = 20
        self.target_details.set_left_margin(margin)
        self.target_details.set_right_margin(margin)
        self.add_button = self.wTree.get_widget('target_add')
        self.edit_button = self.wTree.get_widget('target_edit')
        self.edit_button.set_sensitive(False)
        self.delete_button = self.wTree.get_widget('target_delete')
        self.delete_button.set_sensitive(False)

        self.addedit_dialog = target_addedit.TargetAddEdit(self.wTree)

        # Set up Global Users list
        globaluser_list = self.wTree.get_widget('globaluser_list')
        self.globaluser_store = gtk.ListStore(str, str)
        globaluser_list.set_model(self.globaluser_store)

        user_col = gtk.TreeViewColumn('Username')
        user_cell = gtk.CellRendererText()
        user_col.pack_start(user_cell, True)
        user_col.add_attribute(user_cell, 'text', 0)
        user_col.set_sort_column_id(-1)
        globaluser_list.append_column(user_col)

        user_col = gtk.TreeViewColumn('Password')
        user_cell = gtk.CellRendererText()
        user_col.pack_start(user_cell, True)
        user_col.add_attribute(user_cell, 'text', 1)
        user_col.set_sort_column_id(-1)
        globaluser_list.append_column(user_col)

        globaluser_list.set_search_column(0)
        globaluser_list.set_reorderable(False)

        dic = { 'session_tree_cursor_changed_cb' : self.cursor_changed,
                'target_add_clicked_cb' : self.add_target,
                'target_edit_clicked_cb' : self.edit_target,
                'session_tree_row_activated_cb' : self.edit_target_activate,
                'target_delete_clicked_cb' : self.delete_target,
                'lun_add_clicked_cb' : self.addedit_dialog.add_lun,
                'lun_edit_clicked_cb' : self.addedit_dialog.edit_lun,
                'lun_delete_clicked_cb' : self.addedit_dialog.delete_lun,
                'lun_list_row_activated_cb' : self.addedit_dialog.edit_lun_activate,
                'lun_browse_clicked_cb' : self.addedit_dialog.path_browse_lun,
                'lun_path_activate_cb' : self.addedit_dialog.lun_dialog_ok,
                'option_add_clicked_cb' : self.addedit_dialog.add_option,
                'option_edit_clicked_cb' : self.addedit_dialog.edit_option,
                'option_delete_clicked_cb' : self.addedit_dialog.delete_option,
                'option_list_row_activated_cb' : self.addedit_dialog.edit_option_activate,
                'user_add_clicked_cb' : self.addedit_dialog.add_user,
                'user_edit_clicked_cb' : self.addedit_dialog.edit_user,
                'user_delete_clicked_cb' : self.addedit_dialog.delete_user,
                'user_list_row_activated_cb' : self.addedit_dialog.edit_user_activate,
                'option_name_changed_cb' : self.addedit_dialog.option_changed,
                'allowdeny_type_changed_cb' : self.addedit_dialog.allowdeny_type_changed,
                'allow_list_row_activated_cb' : self.addedit_dialog.edit_allowdeny_activate,
                'deny_list_row_activated_cb' : self.addedit_dialog.edit_allowdeny_activate,
                'add_menu_item_activate_cb' : self.add_target_menu,
                'edit_menu_item_activate_cb' : self.edit_target_menu,
                'delete_menu_item_activate_cb' : self.delete_target_menu,
                'quit_menu_item_activate_cb' : gtk.main_quit,
                'refresh_menu_item_activate_cb' : self.refresh_menu,
                'all_menu_item_activate_cb' : self.allowdeny_menu,
                'options_menu_item_activate_cb' : self.options_menu,
                'globaluser_add_clicked_cb' : self.add_user,
                'globaluser_edit_clicked_cb' : self.edit_user,
                'globaluser_delete_clicked_cb' : self.delete_user,
                'globaluser_list_row_activated_cb' : self.edit_user_activate,
                'isnsserver_check_toggled_cb' : self.toggle_isnsserver,
                'isnsac_check_toggled_cb' : self.toggle_isnsac,
                'outuser_check_toggled_cb' : self.toggle_outuser,
                'isnsac_toggle_toggled_cb' : self.toggle_isnsac_toggle,
                'about_menu_item_activate_cb' : self.about,
                'all_allow_list_row_activated_cb' : self.addedit_dialog.edit_allowdeny_activate,
                'all_deny_list_row_activated_cb' : self.addedit_dialog.edit_allowdeny_activate,
                'scsiid_check_toggled_cb' : self.addedit_dialog.toggle_scsiid,
                'scsisn_check_toggled_cb' : self.addedit_dialog.toggle_scsisn,
                'iomode_check_toggled_cb' : self.addedit_dialog.toggle_iomode
              }

        self.wTree.signal_autoconnect (dic)

        self.deny_store = gtk.ListStore(str)
        self.allow_store = gtk.ListStore(str)

        # Set up initiators.allow table
        self.allow_list = self.wTree.get_widget('all_allow_list')
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
        self.deny_list = self.wTree.get_widget('all_deny_list')
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

        deny_add = self.wTree.get_widget('all_deny_add')
        deny_add.connect('clicked',
                         self.addedit_dialog.add_allowdeny,
                         self.deny_list)

        deny_edit = self.wTree.get_widget('all_deny_edit')
        deny_edit.connect('clicked',
                          self.addedit_dialog.edit_allowdeny,
                          self.deny_list)

        deny_delete = self.wTree.get_widget('all_deny_delete')
        deny_delete.connect('clicked',
                            self.addedit_dialog.delete_allowdeny,
                            self.deny_list)

        allow_add = self.wTree.get_widget('all_allow_add')
        allow_add.connect('clicked',
                          self.addedit_dialog.add_allowdeny,
                          self.allow_list)

        allow_edit = self.wTree.get_widget('all_allow_edit')
        allow_edit.connect('clicked',
                           self.addedit_dialog.edit_allowdeny,
                           self.allow_list)

        allow_delete = self.wTree.get_widget('all_allow_delete')
        allow_delete.connect('clicked',
                             self.addedit_dialog.delete_allowdeny,
                             self.allow_list)

        self.tooltips = gtk.Tooltips()

        # Check that we have root privledges
        if os.geteuid() != 0:
            msg = gtk.MessageDialog(flags = gtk.DIALOG_DESTROY_WITH_PARENT,
                    type = gtk.MESSAGE_WARNING,
                    buttons = gtk.BUTTONS_CLOSE,
                    message_format = 'IETView is not being run with root ' \
                                     'privileges.  Functionality may be ' \
                                     'reduced.')

            response = msg.run()
            msg.destroy()

        self.backup_files()
        self.reload_sessions()

    def run(self):
        gtk.main()

    def refresh_menu(self, menuitem):
        self.reload_sessions()

    def reload_sessions(self):
        path, col = self.target_list.get_cursor()
        if path != None and len(path) in [2, 3]:
            old_tname = self.target_store[path[0:2]][0]
        else:
            old_tname = None
            
        self.target_store.clear()

        self.iets = iet_session.IetSessions(self.SESSION_PATH)
        self.ietv = iet_volume.IetVolumes(self.VOLUME_PATH) 

        try:
            self.iets.parse_file()
            self.ietv.parse_file()
        except IOError, inst:
            msg_str = '%s could not be opened.  Verify that iSCSI ' \
                      'Enterprise Target software is running correctly.\n' \
                      % inst.filename

            msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                     type = gtk.MESSAGE_ERROR,
                     buttons = gtk.BUTTONS_CLOSE,
                     message_format = msg_str)     

            msg.run()
            msg.destroy()

        self.ietc = iet_conf.IetConfFile(self.CONF_FILE_PATH)
        self.ietc.parse_file()

        self.iet_allow = iet_allowdeny.IetAllowDeny(
                                self.INITIATORS_ALLOW_PATH)
        self.iet_allow.parse_file()

        self.iet_deny = iet_allowdeny.IetAllowDeny(
                                self.INITIATORS_DENY_PATH)
        self.iet_deny.parse_file()

        active_targets = self.target_store.append(None,
                                                  ['Active Targets', '',
                                                   '', '', ''])
        
        for session in self.iets.sessions.itervalues():
            piter = self.target_store.append(active_targets,
                                             [ session.target, '',
                                               '', '', ''])

            for client in session.clients.itervalues():
                self.target_store.append(piter,
                           ['%s/%s (%s)' % (client.ip, client.initiator,
                            client.state), client.initiator, client.ip,
                            client.sid, client.cid])

        disabled_targets = self.target_store.append(None,
                                                    ['Disabled Targets', '',
                                                     '', '', ''])

        for target in self.ietc.inactive_targets.itervalues():
            self.target_store.append(disabled_targets, [ target.name, '',
                                                         '', '', ''])

        #Re-highlight the previously selected target.
        if old_tname:
            for row in self.target_store:
                for child_row in row.iterchildren():
                    if old_tname == child_row[0]:
                        self.target_list.expand_to_path(child_row.path)
                        self.target_list.set_cursor(child_row.path)

        self.target_list.expand_row((0), False)

    def backup_files(self):
        sfx = '.ietviewbk'
        paths = [self.CONF_FILE_PATH,
                 self.INITIATORS_DENY_PATH,
                 self.INITIATORS_ALLOW_PATH]

        changed_files = []

        # Backup any files that haven't already been backed up
        # Check that the file exists, and if the backup file doesn't
        # exist or the original and backup are different, then
        # check if the original starts with my signature.
        # If not, then make a copy
        for path in paths:
            if os.path.exists(path) \
               and (not os.path.exists(path + sfx) 
                    or not filecmp.cmp(path, path + sfx)):

                try:
                    f = open(path, 'r')
                    if f.readline() != '# Written by IETView\n':
                        shutil.copyfile(path, path + '.ietviewbk')
                        changed_files.append(path)

                    f.close()
                except IOError:
                    pass

        if changed_files:
            msg_str = "The following file backups were made because it " \
                      "didn't look like the files were written " \
                      "by this program:\n\n"

            for path in changed_files:
                msg_str = msg_str + path + ' ==> ' + path + '.ietviewbk\n'

            msg = gtk.MessageDialog(flags = gtk.DIALOG_DESTROY_WITH_PARENT,
                     type = gtk.MESSAGE_INFO,
                     buttons = gtk.BUTTONS_CLOSE,
                     message_format = msg_str)     

            response = msg.run()
            msg.destroy()

    def disconnect_clients(self, iter):
        if self.target_store.iter_has_child(iter):
            msg_str = "Target has active clients.  Disconnect " \
                      "clients and deactivate it? 'No' abandons edits."

            msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                    type = gtk.MESSAGE_QUESTION,
                                    buttons = gtk.BUTTONS_YES_NO,
                                    message_format = msg_str)

            response = msg.run()
            msg.destroy()

            if response == gtk.RESPONSE_NO:
                return 1
 
        iter = self.target_store.iter_children(iter)

        while iter != None:
            self.disconnect_client(iter, force=True)
            iter = self.target_store.iter_next(iter)

        return 0

    def disconnect_client(self, iter, force=False):
        tname = self.target_store[self.target_store.iter_parent(iter)][0]
        initiator = self.target_store[iter][1]
        ip = self.target_store[iter][2]
        sid = self.target_store[iter][3]
        cid = self.target_store[iter][4]
        key = ip + '/' + initiator + '/' + str(sid) + '/' + str(cid)

        client = self.iets.sessions[tname].clients[key]

        if force:
            adm = ietadm.IetAdm()
            adm.delete_connection(tid=self.iets.sessions[tname].tid,
                                    sid=client.sid,
                                    cid=client.cid)
            return

        msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                type = gtk.MESSAGE_QUESTION,
                                buttons = gtk.BUTTONS_YES_NO,
                                message_format = 'Kill this client?\n%s' \
                                                    % client.initiator)

        response = msg.run()

        if response == gtk.RESPONSE_YES:
            adm = ietadm.IetAdm()
            adm.delete_connection(tid=self.iets.sessions[tname].tid,
                                    sid=client.sid,
                                    cid=client.cid)

            self.reload_sessions()
            self.target_details.set_buffer(gtk.TextBuffer())

        msg.destroy()


    def delete_target_menu(self, menuitem):
        """ Delete Menu Item Clicked """
        self.delete_target(None)

    def delete_target(self, button):
        path, col = self.target_list.get_cursor()
        if path == None or len(path) not in [2, 3]:
            return

        if len(path) == 2:
            #delete a target
            tname = self.target_store[path][0]
            iter = self.target_store.get_iter(path)

            if self.target_store.iter_has_child(iter):
                msg_str = '%s has active clients.  Disconnect ' \
                          'clients and permanently delete it?' % tname
            else:
                msg_str = 'Permanently delete %s?' % tname
                        

            msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                    type = gtk.MESSAGE_QUESTION,
                                    buttons = gtk.BUTTONS_YES_NO,
                                    message_format = msg_str)

            response = msg.run()

            if response == gtk.RESPONSE_YES:
                if self.target_store.iter_has_child(iter):
                    iter = self.target_store.iter_children(iter)

                    while iter != None:
                        self.disconnect_client(iter, force=True)
                        iter = self.target_store.iter_next(iter)

                if path[0] == 0:
                    adm = ietadm.IetAdm()
                    adm.delete_target(self.iets.sessions[tname].tid)

                if tname in self.ietc.targets:
                    del self.ietc.targets[tname]

                if tname in self.ietc.inactive_targets:
                    del self.ietc.inactive_targets[tname]

                if tname in self.iet_deny.targets:
                    del self.iet_deny.targets[tname]

                if tname in self.iet_allow.targets:
                    del self.iet_allow.targets[tname]

                self.commit_files()

            msg.destroy()

        elif len(path) == 3:
            iter = self.target_store.get_iter(path)
            self.disconnect_client(iter)

        self.target_details.set_buffer(gtk.TextBuffer())
        self.reload_sessions()

    def commit_files(self):
        try:
            self.ietc.write()
            self.iet_deny.write()
            self.iet_allow.write()
        except IOError, inst:
            msg_str = 'The following error occurred when attempting to ' \
                      'write to %s\nI\O error(%d): %s' \
                      % (inst.filename, inst.errno, inst.strerror)

            msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                     type = gtk.MESSAGE_ERROR,
                     buttons = gtk.BUTTONS_CLOSE,
                     message_format = msg_str)     

            response = msg.run()
            msg.destroy()

    def get_next_tid(self):
        tids = []

        for session in self.iets.sessions.itervalues():
            tids.append(session.tid)

        tids.sort()

        next_tid = 1
        for tid in tids:
            if tid != next_tid:
                return next_tid

            next_tid += 1

        return next_tid
 
    def add_target_from_dialog(self, tid, active, saved, dialog):
        tname = dialog.tname.get_text()

        if saved:
            self.ietc.add_target(tname, active, **dict(dialog.option_store))
            # TODO: replace with a get in IetConfFile
            if active:
                conf_target = self.ietc.targets[tname]
            else:
                conf_target = self.ietc.inactive_targets[tname]

            idx = 0
            for path, iotype, sid, ssn, io in dialog.lun_store:
                conf_target.add_lun(idx, path, iotype,
                                    scsiid=sid, scsisn=ssn, iomode=io)
                idx += 1

            for user, password in dialog.user_store:
                conf_target.add_user(user, password)

            for host in dialog.deny_store:
                self.iet_deny.add_host(tname, host[0])
    
            for host in dialog.allow_store:
                self.iet_allow.add_host(tname, host[0])
    
        if active:
            adm = ietadm.IetAdm()
            adm.add_target(tid, tname)
    
            for key, value in dialog.option_store:
                adm.add_option(tid, key, value)
    
            idx = 0
            for path, iotype, sid, ssn, io in dialog.lun_store:
                adm.add_lun(tid, lun=idx, path=path, type=iotype, scsiid=sid,
                            scsisn=ssn, iomode=io)
                idx += 1
    
            for user, password in dialog.user_store:
                adm.add_user(tid, user, password)
    
            for host in dialog.deny_store:
                self.iet_deny.add_host(tname, host[0])
    
            for host in dialog.allow_store:
                self.iet_allow.add_host(tname, host[0])

    def add_target_menu(self, menuitem):
        """ Add Menu Item Clicked """
        self.add_target(None)
   
    def add_target(self, button):
        response = self.addedit_dialog.run_add()

        if response != 1:
            return

        active = self.addedit_dialog.active.get_active()
        saved = self.addedit_dialog.saved.get_active()
        tid = self.get_next_tid()
        self.add_target_from_dialog(tid, active, saved, self.addedit_dialog)
   
        self.commit_files()
        self.reload_sessions()

    def edit_target_menu(self, menuitem):
        """ Edit Menu Item Clicked """
        self.edit_target(None)
     
    def edit_target_activate(self, tree, path, col):
        """ Double click triggers an edit """
        self.edit_target(None)

    def edit_target(self, button):
        path, col = self.target_list.get_cursor()
        if path == None:
            return
        
        if len(path) != 2:
            return

        active = (1,0)[path[0]]

        target = self.target_store[path][0]

        if active:
            session = self.iets.sessions[target]
            vol = self.ietv.volumes[session.tid]

            if target in self.ietc.targets:
                conf = self.ietc.targets[target]
                saved = True
            else:
                conf = None
                saved = False
        else:
            session = None
            vol = None

            if target in self.ietc.inactive_targets:
                conf = self.ietc.inactive_targets[target]
                saved = True
            else:
                conf = None
                saved = False
 
        if target in self.iet_allow.targets:
            allow = self.iet_allow.targets[target]
        else:
            allow = []

        if target in self.iet_deny.targets:
            deny = self.iet_deny.targets[target]
        else:
            deny = []

        old = iet_target.IetTarget(tname=target, active=active, saved=saved,
                session=session, vol=vol, allow=allow, deny=deny, conf=conf) 

        response = self.addedit_dialog.run_edit(active=active, vol=vol,
                allow=allow, deny=deny, conf=conf, session=session)

        if response != 1:
            return

        new_target = iet_target.IetTarget(dialog=self.addedit_dialog)

        diff = old.diff(right=new_target)

        #TODO: target name change (or disable this field on edit active)

        adm = ietadm.IetAdm()

        for op, type, val in diff:
            if type == 'active' and val == False:
                iter = self.target_store.get_iter(path)
                if self.disconnect_clients(iter):
                    return

                adm.delete_target(old.tid)
                self.ietc.disable_target(old)
                active = False
                old.active = False

        for op, type, val in diff:
            if type == 'saved' and val == False:
                self.ietc.delete_target(old.name, old.active)
                saved = False

        if active:
            adm.update(old, diff)

        self.iet_allow.update(old, diff, 'allow')
        self.iet_deny.update(old, diff, 'deny')

        if saved:
            self.ietc.update(old, diff)

        for op, type, val in diff:
            if type == 'active' and val == True:
                tid = self.get_next_tid()
                self.add_target_from_dialog(tid, True, saved,
                                            self.addedit_dialog)

                self.ietc.activate_target(old)
            elif type == 'saved' and val == True:
                self.add_target_from_dialog(old.tid, active, True,
                                            self.addedit_dialog)

        self.commit_files()
        self.reload_sessions()

    def show_lun_details(self, lun, buf):
        buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                        '\tLUN ID: ', 'Bold')

        buf.insert(buf.get_end_iter(), str(lun.number) + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                        '\tIO Type: ', 'Bold')

        buf.insert(buf.get_end_iter(), lun.iotype + '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                        '\tPath: ', 'Bold')
        
        buf.insert(buf.get_end_iter(), lun.path + '\n')

        for option in ['SCSI ID', 'SCSI SN', 'IO Mode', 'State']:
            key = option.replace(' ', '').lower()

            if key in lun.options:
                buf.insert_with_tags_by_name(buf.get_end_iter(), 
                                            '\t%s: ' % option, 'Bold')
                buf.insert(buf.get_end_iter(), str(lun.options[key]) + '\n')

    def show_session_details(self, path):
        target = self.target_store[path][0]
        tid = self.iets.sessions[target].tid

        buf = gtk.TextBuffer()
        buf.create_tag('Heading', scale=pango.SCALE_X_LARGE,
                                  weight=pango.WEIGHT_BOLD,
                                  variant=pango.VARIANT_SMALL_CAPS)

        buf.create_tag('Heading2', scale=pango.SCALE_LARGE)
        buf.create_tag('Heading3', scale=pango.SCALE_LARGE,
                                   paragraph_background='grey')

        buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     '\nDetails for Target\n', 'Heading')

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     '%s\n\n' % target, 'Heading2')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Name: ', 'Bold')
        buf.insert(buf.get_end_iter(), target + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Target ID: ', 'Bold')
        buf.insert(buf.get_end_iter(), str(tid) + '\n')

        buf.insert(buf.get_end_iter(), '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'LUNS\n', 'Heading3')
        vol = self.ietv.volumes[tid]
        first = 1
        for lk in sorted(vol.luns.iterkeys()):
            lun = vol.luns[lk]

            if first:
                first = 0
            else:
                buf.insert(buf.get_end_iter(), '\n')

            if target in self.ietc.targets \
               and lun.number in self.ietc.targets[target].luns:
                conf_lun = self.ietc.targets[target].luns[lun.number]
                # Bit of a hack until I restructure things
                options = {}
                for key, val in conf_lun.options.iteritems():
                    options[key] = val

                for key, val in lun.options.iteritems():
                    options[key] = val

                old_options = lun.options
                lun.options = options
                self.show_lun_details(lun, buf)
                lun.options = old_options
            else:
                self.show_lun_details(lun, buf)

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Deny\n', 'Heading3')

        if target in self.iet_deny.targets:
            hosts = self.iet_deny.targets[target]
            for host in hosts:
                buf.insert(buf.get_end_iter(), '\t' + host + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Allow\n', 'Heading3')

        if target in self.iet_allow.targets:
            hosts = self.iet_allow.targets[target]
            for host in hosts:
                buf.insert(buf.get_end_iter(), '\t' + host + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        if target in self.ietc.targets:
            buf.insert(buf.get_end_iter(), '\n')
            buf.insert_with_tags_by_name(buf.get_end_iter(),
                                        'Incoming Users\n', 'Heading3')

            for uname, passwd in self.ietc.targets[target].users.iteritems():
                buf.insert(buf.get_end_iter(), '\t%s/%s\n' % (uname, passwd))

            if len(self.ietc.targets[target].users) == 0:
                buf.insert(buf.get_end_iter(), '\n')

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Options\n', 'Heading3')
        adm = ietadm.IetAdm()
        params = {}
        adm.show(params, tid, sid=0)
        for key in sorted(params.iterkeys()):
            buf.insert_with_tags_by_name(buf.get_end_iter(), '\t' + key, 'Bold')
            buf.insert(buf.get_end_iter(), ': %s\n' % params[key])

        self.target_details.set_buffer(buf)

    def show_client_details(self, path):
        target = self.target_store[path[0:2]][0]
        initiator = self.target_store[path][1]
        ip = self.target_store[path][2]
        sid = self.target_store[path][3]
        cid = self.target_store[path][4]
        key = ip + '/' + initiator + '/' + str(sid) + '/' + str(cid)
        client = self.iets.sessions[target].clients[key]
        buf = gtk.TextBuffer()
        buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)
        buf.create_tag('Heading', scale=pango.SCALE_X_LARGE,
                                  weight=pango.WEIGHT_BOLD, 
                                  variant=pango.VARIANT_SMALL_CAPS)

        buf.create_tag('Heading2', scale=pango.SCALE_LARGE)
        buf.create_tag('Heading3', scale=pango.SCALE_LARGE,
                                   paragraph_background='grey')

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     '\nDetails for Connection\n', 'Heading')
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     '%s\n\n' % client.initiator, 'Heading2')

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Initiator Name: ', 'Bold')
        buf.insert(buf.get_end_iter(), client.initiator + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'IP: ', 'Bold')
        buf.insert(buf.get_end_iter(), client.ip + '\n')
        
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Connection State: ', 'Bold')
        buf.insert(buf.get_end_iter(), client.state + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Session ID: ', 'Bold')
        buf.insert(buf.get_end_iter(), str(client.sid) + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Connection ID: ', 'Bold')
        buf.insert(buf.get_end_iter(), str(client.cid) + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Header Digest State: ', 'Bold')
        buf.insert(buf.get_end_iter(), client.hd + '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Data Digest State: ', 'Bold')
        buf.insert(buf.get_end_iter(), client.dd + '\n')

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Session Parameters\n', 'Heading3')
        adm = ietadm.IetAdm()
        params = {}
        adm.show(params, self.iets.sessions[target].tid, client.sid)
        keys = params.keys()
        keys.sort()
        for key in keys:
            buf.insert_with_tags_by_name(buf.get_end_iter(), '\t' + key, 'Bold')
            buf.insert(buf.get_end_iter(), ': %s\n' % params[key])

        self.target_details.set_buffer(buf)

    def show_config_details(self, path):
        tname = self.target_store[path][0]
        target = self.ietc.inactive_targets[tname]

        buf = gtk.TextBuffer()
        buf.create_tag('Heading', scale=pango.SCALE_X_LARGE,
                                  weight=pango.WEIGHT_BOLD,
                                  variant=pango.VARIANT_SMALL_CAPS)

        buf.create_tag('Heading2', scale=pango.SCALE_LARGE)
        buf.create_tag('Heading3', scale=pango.SCALE_LARGE,
                                   paragraph_background='grey')
        buf.create_tag('Bold', weight=pango.WEIGHT_BOLD)

        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     '\nDetails for Target\n', 'Heading')
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     '%s\n\n' % tname, 'Heading2')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Name: ', 'Bold')
        buf.insert(buf.get_end_iter(), tname + '\n')
        buf.insert(buf.get_end_iter(), '\n')

        buf.insert_with_tags_by_name(buf.get_end_iter(), 'LUNS\n', 'Heading3')
        first = 1
        for lk in sorted(target.luns.iterkeys()):
            lun = target.luns[lk]

            if first:
                first = 0
            else:
                buf.insert(buf.get_end_iter(), '\n')

            self.show_lun_details(lun, buf)

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Deny\n', 'Heading3')

        if tname in self.iet_deny.targets:
            hosts = self.iet_deny.targets[tname]
            for host in hosts:
                buf.insert(buf.get_end_iter(), '\t' + host + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(), 'Allow\n', 'Heading3')

        if tname in self.iet_allow.targets:
            hosts = self.iet_allow.targets[tname]
            for host in hosts:
                buf.insert(buf.get_end_iter(), '\t' + host + '\n')
        else:
            buf.insert(buf.get_end_iter(), '\n')

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Incoming Users\n', 'Heading3')

        for uname, passwd in target.users.iteritems():
            buf.insert(buf.get_end_iter(), '\t%s/%s\n' % (uname, passwd))

        buf.insert(buf.get_end_iter(), '\n')
        buf.insert_with_tags_by_name(buf.get_end_iter(),
                                     'Options\n', 'Heading3')

        for key, value in target.options.iteritems():
            buf.insert_with_tags_by_name(buf.get_end_iter(), '\t' + key, 'Bold')
            buf.insert(buf.get_end_iter(), ': %s\n' % value)

        self.target_details.set_buffer(buf)

    def cursor_changed(self, target_list):
        path, col = target_list.get_cursor()
        edit_menu = self.wTree.get_widget('edit_menu_item')
        delete_menu = self.wTree.get_widget('delete_menu_item')
        
        if path == None:
            return
        
        if len(path) == 1:
            # Clicked on Active Targets or Disabled targets
            self.delete_button.set_sensitive(False)
            delete_menu.set_sensitive(False)
            self.edit_button.set_sensitive(False)
            edit_menu.set_sensitive(False)
            self.target_details.set_buffer(gtk.TextBuffer())
        elif len(path) == 2:
            # Clicked on target
            if path[0] == 0:
                self.show_session_details(path)
            elif path[0] == 1:
                self.show_config_details(path)

            self.delete_button.set_sensitive(True)
            delete_menu.set_sensitive(True)
            self.tooltips.set_tip(self.delete_button, 'Delete the selected target')
            self.edit_button.set_sensitive(True)
            edit_menu.set_sensitive(True)
        else:
            # Clicked on a client
            self.show_client_details(path)
            self.delete_button.set_sensitive(True)
            self.tooltips.set_tip(self.delete_button, 'Delete the selected connection')
            delete_menu.set_sensitive(True)
            self.edit_button.set_sensitive(False)
            edit_menu.set_sensitive(False)

    def bold_cell(self, col, cell, model, iter):
        ''' Bolds Active and Disabled target row text '''
        path = model.get_path(iter)
        if len(path) == 1:
            cell.set_property('weight', pango.WEIGHT_BOLD)
            cell.set_property('scale', pango.SCALE_LARGE)
        else:
            cell.set_property('weight', pango.WEIGHT_NORMAL)
            cell.set_property('scale', pango.SCALE_MEDIUM)

    def toggle_isnsserver(self, button):
        entry = self.wTree.get_widget('isnsserver_entry')

        entry.set_sensitive(button.get_active())

    def toggle_isnsac(self, button):
        entry = self.wTree.get_widget('isnsac_toggle')

        entry.set_sensitive(button.get_active())

    def toggle_outuser(self, button):
        user_entry = self.wTree.get_widget('outuser_name')
        pass_entry = self.wTree.get_widget('outuser_pass')
        user_entry.set_sensitive(button.get_active())
        pass_entry.set_sensitive(button.get_active())

    def toggle_isnsac_toggle(self, button):
        if button.get_active():
            button.set_label('Yes')
        else:
            button.set_label('No')
 
    def allowdeny_menu(self, menuitem):
        allowdeny_menu = self.wTree.get_widget('global_allowdeny_dialog')

        self.allow_store.clear()
        if 'ALL' in self.iet_allow.targets:
            for host in self.iet_allow.targets['ALL']:
                self.allow_store.append([host])

        self.deny_store.clear()
        if 'ALL' in self.iet_deny.targets:
            for host in self.iet_deny.targets['ALL']:
                self.deny_store.append([host])

        response = allowdeny_menu.run()
        allowdeny_menu.hide()

        if response == 1:
            allow_hosts = []

            for row in self.allow_store:
                allow_hosts.append(row[0])

            if len(allow_hosts) > 0:
                self.iet_allow.targets['ALL'] = allow_hosts

            deny_hosts = []

            for row in self.deny_store:
                deny_hosts.append(row[0])

            if len(deny_hosts) > 0:
                self.iet_deny.targets['ALL'] = deny_hosts

            self.commit_files()

    def options_menu(self, menuitem):
        options_menu = self.wTree.get_widget('global_options_dialog')
        user_list = self.wTree.get_widget('globaluser_list')
        isnsserver_check = self.wTree.get_widget('isnsserver_check')
        isnsserver_entry = self.wTree.get_widget('isnsserver_entry')
        isnsac_check = self.wTree.get_widget('isnsac_check')
        isnsac_toggle = self.wTree.get_widget('isnsac_toggle')
        outuser_check = self.wTree.get_widget('outuser_check')
        user_entry = self.wTree.get_widget('outuser_name')
        pass_entry = self.wTree.get_widget('outuser_pass')

        self.globaluser_store.clear()

        isnsserver_check.set_active(False)
        isnsac_check.set_active(False)
        outuser_check.set_active(False)

        for key, val in self.ietc.options.iteritems():
            if key == 'OutgoingUser':
                outuser_check.set_active(True)
                user, passwd = val.split('/')
                user_entry.set_text(user)
                pass_entry.set_text(passwd)
            elif key == 'iSNSServer':
                isnsserver_check.set_active(True)
                isnsserver_entry.set_text(val)
            elif key == 'iSNSAccessControl':
                isnsac_check.set_active(True)
                isnsac_toggle.set_active(val == 'Yes')

        for user, passwd in self.ietc.users.iteritems():
            self.globaluser_store.append([user, passwd])

        response = options_menu.run()
        options_menu.hide()

        if response == 1:
            warning = 0
            active = isnsserver_check.get_active()
            key = 'iSNSServer'
            val = isnsserver_entry.get_text()

            if active:
                if key not in self.ietc.options \
                   or val != self.ietc.options[key]:

                    warning = 1

                self.ietc.options[key] = val
            elif key in self.ietc.options:
                del self.ietc.options[key]
                warning = 1

            active = isnsac_check.get_active()
            key = 'iSNSAccessControl'
            if isnsac_toggle.get_active():
                val = 'Yes'
            else:
                val = 'No'

            if active:
                if key not in self.ietc.options \
                   or val != self.ietc.options[key]:

                    warning = 1

                self.ietc.options[key] = val
            elif key in self.ietc.options:
                del self.ietc.options[key]
                warning = 1

            active = outuser_check.get_active()
            key = 'OutgoingUser'
            val = user_entry.get_text() + '/' + pass_entry.get_text()
            adm = ietadm.IetAdm()

            if active:
                if key not in self.ietc.options:
                    adm.add_option(-1, key, val)
                elif val != self.ietc.options[key]:
                    adm.delete_option(-1, key, val)
                    adm.add_option(-1, key, val)

                self.ietc.options[key] = val
            elif key in self.ietc.options:
                adm.delete_option(-1, key, val)
                del self.ietc.options[key]

            newusers = {}
            for uname, passwd in self.globaluser_store:
                newusers[uname] = passwd

                if uname not in self.ietc.users:
                    self.ietc.users[uname] = passwd
                    adm.add_user(-1, uname, passwd)
                elif passwd != self.ietc.users[uname]:
                    self.ietc.users[uname] = passwd
                    adm.delete_user(-1, uname)
                    adm.add_user(-1, uname, passwd)

            for uname, passwd in self.ietc.users.items():
                if uname not in newusers:
                    adm.delete_user(-1, uname)
                    del self.ietc.users[uname]

            self.commit_files()

            if warning:
                msg = gtk.MessageDialog(flags = gtk.DIALOG_DESTROY_WITH_PARENT,
                        type = gtk.MESSAGE_WARNING,
                        buttons = gtk.BUTTONS_CLOSE,
                        message_format = 'Changes related iSNS will ' \
                                         'only take effect after ' \
                                         'iscsi-target has been restarted.')

                response = msg.run()
                msg.destroy()

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
            self.globaluser_store.append([user_name.get_text(),
                                    user_password.get_text()])

    def edit_user_activate(self, treeview, path, col):
        return self.edit_user(None)

    def edit_user(self, button):
        user_addedit = self.wTree.get_widget('user_addedit_dialog')
        user_name = self.wTree.get_widget('user_name')
        user_password = self.wTree.get_widget('user_password')
        user_list = self.wTree.get_widget('globaluser_list')

        path, col = user_list.get_cursor()
        if path == None:
            return

        user, passwd = self.globaluser_store[path]

        user_name.set_text(user)
        user_name.grab_focus()
        user_password.set_text(passwd)


        response = user_addedit.run()
        user_addedit.hide()

        if response == 1:
            #TODO: validate input
            self.globaluser_store[path] = [user_name.get_text(),
                                     user_password.get_text()]

    def delete_user(self, button):
        user_list = self.wTree.get_widget('globaluser_list')
        path, col = user_list.get_cursor()
        if path == None:
            return

        user = self.globaluser_store[path][0]

        msg = gtk.MessageDialog(flags = gtk.DIALOG_MODAL,
                                type = gtk.MESSAGE_QUESTION,
                                buttons = gtk.BUTTONS_YES_NO,
                                message_format = 'Delete this user?\n%s' % user)

        response = msg.run()

        if response == gtk.RESPONSE_YES:
            del self.globaluser_store[path]

        msg.destroy()

    def about(self, menuitem):
        about = self.wTree.get_widget('about_dialog')
        about.set_name('IETView')
        about.run()
        about.hide()

if __name__ == '__main__':
    iet_view = IetView()
    iet_view.run()
