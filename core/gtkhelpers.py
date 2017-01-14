#!/usr/bin/python
#
# The Qubes OS Project, https://www.qubes-os.org/
#
# Copyright (C) 2017 boring-stuff <boring-stuff@users.noreply.github.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GdkPixbuf

gladeDirectory = os.path.join(os.path.dirname(__file__),"gtk")

class TransferWindow():
    _sourceFile = os.path.join(gladeDirectory, "TransferWindow.glade")
    _sourceId = { 'window': "TransferWindow", 
                  'ok': "okButton", 
                  'cancel': "cancelButton", 
                  'description': "TransferDescription", 
                  'target': "TargetCombo",
                }
    _textDescription = "Allow domain '<b>%s</b>' to execute a file transfer?\n<small>Select the target domain and confirm with 'OK'.</small>"

    def _clickedOk(self, button):
        self._confirmed = True
        self._close()
	    
    def _clickedCancel(self, button):
        self._confirmed = False
        self._close()

    def __init__(self, source, target = None):
        self._gtkBuilder = Gtk.Builder()
        self._gtkBuilder.add_from_file(self._sourceFile)
        self._transferWindow = self._gtkBuilder.get_object(self._sourceId['window'])
        self._transferOkButton = self._gtkBuilder.get_object(self._sourceId['ok'])
        self._transferCancelButton = self._gtkBuilder.get_object(self._sourceId['cancel'])
        self._transferDescriptionLabel = self._gtkBuilder.get_object(self._sourceId['description'])
        self._transferComboBox = self._gtkBuilder.get_object(self._sourceId['target'])
        
        self._vmListModeler = self._newVMListModeler()
        
        self._transferDescriptionLabel.set_markup(self._textDescription % source)
        self._transferOkButton.connect("clicked", self._clickedOk)
        self._transferCancelButton.connect("clicked", self._clickedCancel)
        self._confirmed = None
        self.targetId = None
        self.targetName = None
		
        self._transferOkButton.set_sensitive(True)
        
        self._vmListModeler.applyModelTo(self._transferComboBox)
        
    def _close(self):
        self._transferWindow.close()
		
    def _show(self):
        self._transferWindow.connect("delete-event", Gtk.main_quit)
        self._transferWindow.show_all()
		
        Gtk.main()

    def _newVMListModeler(self):
        return VMListModeler()

    def confirmTransfer(self):
        self._show()
        
        if self._confirmed:
            return { 'targetId': self._targetId, 'targetName': self._targetName }
        else:
            return False

#TODO Import me instead
class QubesVmLabel(object):
    def __init__(self, index, color, name, dispvm=False):
        self.index = index
        self.color = color
        self.name = name
        self.dispvm = dispvm

        self.icon = '{}-{}'.format(('dispvm' if dispvm else 'appvm'), name)

    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, dispvm={!r})'.format(
            self.__class__.__name__,
            self.index,
            self.color,
            self.name,
            self.dispvm)

    # self.icon_path is obsolete
    # use QIcon.fromTheme(label.icon) where applicable
    @property
    def icon_path(self):
        return os.path.join(system_path['qubes_icon_dir'], self.icon) + ".png"


class VMListModeler:
    def __init__(self):
        self._loadList()
        
    def _loadList(self):
        #TODO load the list instead
        self._list = [QubesVmLabel(0, "red", "sys-net"), QubesVmLabel(1, "red", "sys-firewall"), QubesVmLabel(2, "red", "sys-whonix"), QubesVmLabel(3, "green", "personal"), QubesVmLabel(4, "orange", "anon"), QubesVmLabel(8, "red", "disp-2", True)] 
        
    def applyModelTo(self, destinationObject):
        listStore = Gtk.ListStore(int, str, GdkPixbuf.Pixbuf)

        for vmLabel in self._list:
            path=os.path.dirname(__file__)+"/../../qubes-core-admin-linux/icons/" + vmLabel.color + ".png"
        
            picture = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 32, 32)
            listStore.append([vmLabel.index, vmLabel.name, picture])

        destinationObject.set_model(listStore)

        renderer = Gtk.CellRendererPixbuf()
        destinationObject.pack_start(renderer, False)
        destinationObject.add_attribute(renderer, "pixbuf", 2)
        
        renderer = Gtk.CellRendererText()
        destinationObject.pack_start(renderer, False)
        destinationObject.add_attribute(renderer, "text", 1)
        
if __name__ == "__main__":
    TransferWindow("source").confirmTransfer()
