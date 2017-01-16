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

glade_directory = os.path.join(os.path.dirname(__file__), "gtk")
icons_directory = os.path.join(os.path.dirname(__file__), "../../" +
                    "qubes-core-admin-linux/icons/")

class TransferWindow():
    _source_file = os.path.join(glade_directory, "TransferWindow.glade")
    _source_id = { 'window': "TransferWindow", 
                  'ok': "okButton", 
                  'cancel': "cancelButton", 
                  'description': "TransferDescription", 
                  'target': "TargetCombo",
                }
    _text_description = "Allow domain '<b>%s</b>' to execute a file transfer?" 
    _text_description += "\n<small>Select the target domain and confirm with " 
    _text_description += "'OK'.</small>"

    def _clicked_ok(self, button):
        self._confirmed = True
        self._close()
	    
    def _clicked_cancel(self, button):
        self._confirmed = False
        self._close()

    def _update_ok_button_sensitivity(self, widget = None):
        selection = self._transfer_combo_box.get_active_iter()
        selected = (selection != None)
    
        if (selected):
            model = self._transfer_combo_box.get_model()
            self._target_id = model[selection][0]
            self._target_name = model[selection][1]
        else:
            self._target_id = None
            self._target_name = None

        self._transfer_ok_button.set_sensitive(selected)

    def __init__(self, source, target = None):
        self._gtk_builder = Gtk.Builder()
        self._gtk_builder.add_from_file(self._source_file)
        self._transfer_window = self._gtk_builder.get_object(
                                            self._source_id['window'])
        self._transfer_ok_button = self._gtk_builder.get_object(
                                            self._source_id['ok'])
        self._transfer_cancel_button = self._gtk_builder.get_object(
                                            self._source_id['cancel'])
        self._transfer_description_label = self._gtk_builder.get_object(
                                            self._source_id['description'])
        self._transfer_combo_box = self._gtk_builder.get_object(
                                            self._source_id['target'])
        
        self._transfer_description_label.set_markup(self._text_description 
                                                        % source)
        self._transfer_ok_button.connect("clicked", self._clicked_ok)
        self._transfer_cancel_button.connect("clicked", self._clicked_cancel)
        self._transfer_combo_box.connect("changed", 
                                            self._update_ok_button_sensitivity)
        self._confirmed = None
        self.target_id = None
        self.target_name = None
        
        self._new_VM_list_modeler().apply_model(self._transfer_combo_box, 
                                [ VMListModeler.ExcludeNameFilter(source) ])
        
        self._update_ok_button_sensitivity()
        
    def _close(self):
        self._transfer_window.close()
		
    def _show(self):
        self._transfer_window.connect("delete-event", Gtk.main_quit)
        self._transfer_window.show_all()
		
        Gtk.main()

    def _new_VM_list_modeler(self):
        return VMListModeler()

    def confirm_transfer(self):
        self._show()
        
        if self._confirmed:
            return {    'target_id': self._target_id, 
                        'target_name': self._target_name }
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
        self._load_list()
        
    def _load_list(self):
        #TODO load the list instead
        self._list = [  QubesVmLabel(0, "red", "sys-net"), 
                        QubesVmLabel(1, "red", "sys-firewall"), 
                        QubesVmLabel(2, "red", "source"), 
                        QubesVmLabel(3, "green", "personal"), 
                        QubesVmLabel(4, "orange", "anon"), 
                        QubesVmLabel(8, "red", "disp2", True) ] 
        
    def apply_model(self, destination_object, vm_filter_list = [] ):
        if isinstance(destination_object, Gtk.ComboBox):
            list_store = Gtk.ListStore(int, str, GdkPixbuf.Pixbuf)

            for vm_label in self._list:
                matches = True
                
                for vm_filter in vm_filter_list:
                    if not vm_filter.matches(vm_label):
                        matches = False
                        break
                
                if matches:
                    path = os.path.join(icons_directory, 
                                        vm_label.color + ".png")
            
                    picture = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 32, 32)
                
                    list_store.append([vm_label.index, vm_label.name, picture])

            destination_object.set_model(list_store)

            renderer = Gtk.CellRendererPixbuf()
            destination_object.pack_start(renderer, False)
            destination_object.add_attribute(renderer, "pixbuf", 2)
            
            renderer = Gtk.CellRendererText()
            destination_object.pack_start(renderer, False)
            destination_object.add_attribute(renderer, "text", 1)
        else:
            raise TypeError("Only expecting Gtk.ComboBox objects to want our model.")
        
    class ExcludeNameFilter:
        def __init__(self, avoid_name):
            self._avoid_name = avoid_name
        
        def matches(self, vm_label):
            return vm_label.name != self._avoid_name
            
if __name__ == "__main__":
    print TransferWindow("source").confirm_transfer()
