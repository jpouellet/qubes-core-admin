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
        
        self._transferDescriptionLabel.set_markup(self._textDescription % source)
        
        self._transferOkButton.connect("clicked", self._clickedOk)
        self._transferCancelButton.connect("clicked", self._clickedCancel)
        self._confirmed = None
        self.targetId = None
        self.targetName = None
		
        self._transferOkButton.set_sensitive(True)
        
    def _close(self):
        self._transferWindow.close()
		
    def _show(self):
        self._transferWindow.connect("delete-event", Gtk.main_quit)
        self._transferWindow.show_all()
		
        Gtk.main()


    def confirmTransfer(self):
        self._show()
        
        if self._confirmed:
            return { 'targetId': self._targetId, 'targetName': self._targetName }
        else:
            return False

if __name__ == "__main__":
    TransferWindow("source").confirmTransfer()
