import gtk
import iet_session
import iet_volume
import iet_allowdeny
import iet_conf

class TargetManager(object):

    def __init__(self, session_path, volume_path, conf_file_path,
            initiators_allow_path, initiators_deny_path):
        self.iets = iet_session.IetSessions(session_path)
        self.ietv = iet_volume.IetVolumes(volume_path)

        self.ietc = iet_conf.IetConfFile(conf_file_path)

        self.iet_allow = iet_allowdeny.IetAllowDeny(
                                initiators_allow_path)

        self.iet_deny = iet_allowdeny.IetAllowDeny(
                                initiators_deny_path)

    def parse_file(self):
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

        self.ietc.parse_file()
        self.iet_allow.parse_file()
        self.iet_deny.parse_file()

    def get_all_lun_path(self):
        volumes = self.ietv.volumes
        paths = []

        for key in volumes:
            luns = volumes[key].luns
            paths.extend([luns[i].path for i in luns])

        for v in self.ietc.inactive_targets.itervalues():
            luns = v.luns
            paths.extend([luns[i].path for i in luns])

        return paths

    def path_belong(self, path):
        vols = self.ietv.volumes
        belongs = {}
        for vid in vols:
            lun_ids = vols[vid].get_lun_ids_by_path(path)
            if len(lun_ids) > 0:
                belongs[vols[vid].target] = lun_ids

        for v in self.ietc.inactive_targets.itervalues():
            lun_ids = v.get_lun_ids_by_path(path)
            if len(lun_ids) > 0:
                belongs[v.name] = lun_ids

        return belongs

