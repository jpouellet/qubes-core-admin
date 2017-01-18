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

import qubes

import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GdkPixbuf

glade_directory = os.path.join(os.path.dirname(__file__), "gtk")

class RPCConfirmationWindow():
    _source_file = os.path.join(glade_directory, "RPCConfirmationWindow.glade")
    _source_id = { 'window': "RPCConfirmationWindow", 
                  'ok': "okButton", 
                  'cancel': "cancelButton", 
                  'description': "rpcDescription", 
                  'target': "TargetCombo",
                  'error_bar': "ErrorBar",
                  'error_message': "ErrorMessage",
                }
    _text_description = "Allow domain '<b>%s</b>' to execute the <b>%s</b> "
    _text_description += "operation?\n<small>Select the target domain and " 
    _text_description += "confirm with 'OK'.</small>"

    def _clicked_ok(self, button):
        self._confirmed = True
        self._close()
	    
    def _clicked_cancel(self, button):
        self._confirmed = False
        self._close()

    def _update_ok_button_sensitivity(self, widget = None):
        selection = self._rpc_combo_box.get_active_iter()
        selected = (selection != None)

        if (selected):
            model = self._rpc_combo_box.get_model()
            self._target_id = model[selection][0]
            self._target_name = model[selection][1]
        else:
            self._target_id = None
            self._target_name = None

        self._rpc_ok_button.set_sensitive(selected)

    def _show_error(self, error_message):
        self._error_message.set_text(error_message)
        self._error_bar.set_visible(True)

    def _close_error(self, error_bar, response):
        self._error_bar.set_visible(False)

    def _set_initial_target(self, source, target):
        if target != None:
            if target == source:
                self._show_error(
                     "Source and target domains must not be the same.")
            else:
                model = self._rpc_combo_box.get_model()
                
                found = False
                for item in model:
                    if item[1] == target:
                        found = True
                        
                        self._rpc_combo_box.set_active_iter(
                                    model.get_iter(item.path))
                        
                        break

                if not found:
                    self._show_error("Domain '%s' doesn't exist." % target)

    def __init__(self, source, rpc_operation, target = None):
        self._gtk_builder = Gtk.Builder()
        self._gtk_builder.add_from_file(self._source_file)
        self._rpc_window = self._gtk_builder.get_object(
                                            self._source_id['window'])
        self._rpc_ok_button = self._gtk_builder.get_object(
                                            self._source_id['ok'])
        self._rpc_cancel_button = self._gtk_builder.get_object(
                                            self._source_id['cancel'])
        self._rpc_description_label = self._gtk_builder.get_object(
                                            self._source_id['description'])
        self._rpc_combo_box = self._gtk_builder.get_object(
                                            self._source_id['target'])
        self._error_bar = self._gtk_builder.get_object(
                                            self._source_id['error_bar'])
        self._error_message = self._gtk_builder.get_object(
                                            self._source_id['error_message'])
        
        self._rpc_description_label.set_markup(self._text_description 
                                                    % (source, rpc_operation))
        self._rpc_ok_button.connect("clicked", self._clicked_ok)
        self._rpc_cancel_button.connect("clicked", self._clicked_cancel)
        
        self._error_bar.connect("response", self._close_error)
        
        self._new_VM_list_modeler().apply_model(self._rpc_combo_box, 
                                [ VMListModeler.ExcludeNameFilter("dom0"),
                                  VMListModeler.ExcludeNameFilter(source) ])
        
        self._confirmed = None

        self._set_initial_target(source, target)
        
        self._rpc_combo_box.connect("changed", 
                                    self._update_ok_button_sensitivity)
        self._update_ok_button_sensitivity()
        
    def _close(self):
        self._rpc_window.close()
		
    def _show(self):
        self._rpc_window.connect("delete-event", Gtk.main_quit)
        self._rpc_window.show_all()
		
        Gtk.main()

    def _new_VM_list_modeler(self):
        return VMListModeler()

    def _confirm_rpc(self):
        self._show()
        
        if self._confirmed:
            return {    'target_id': self._target_id, 
                        'target_name': self._target_name }
        else:
            return False
            
    @staticmethod
    def confirm_rpc(source, rpc_operation, target = None):
        window = RPCConfirmationWindow(source, rpc_operation, target)
        
        return window._confirm_rpc()

class GtkIconGetter:
    def __init__(self, size):
        self._icons = {}
        self._size = size
        self._theme = Gtk.IconTheme.get_default()
        
    def get_icon(self, name):
        if name not in self._icons:
            try:
                icon = self._theme.load_icon(name, self._size, 0)
            except:
                icon = self._theme.load_icon("gnome-foot", self._size, 0)
            
            self._icons[name] = icon
            
        return self._icons[name] 

class VMListModeler:
    def __init__(self):
        self._load_list()
        self._icon_getter = GtkIconGetter(32)
        
    def _get_icon(self, vm):
        return self._icon_getter.get_icon(vm.label.icon)
        
    def _load_list(self):
        collection = qubes.QubesVmCollection()
        try:
            collection.lock_db_for_reading()
            
            collection.load()
            
            self._list = [ vm for vm in collection.values() ]
        finally:
            collection.unlock_db()
        
    def apply_model(self, destination_object, vm_filter_list = [] ):
        if isinstance(destination_object, Gtk.ComboBox):
            list_store = Gtk.ListStore(int, str, GdkPixbuf.Pixbuf)

            for vm in self._list:
                matches = True
                
                for vm_filter in vm_filter_list:
                    if not vm_filter.matches(vm):
                        matches = False
                        break
                
                if matches:
                    list_store.append([vm.qid, vm.name, self._get_icon(vm)])

            destination_object.set_model(list_store)

            renderer = Gtk.CellRendererPixbuf()
            destination_object.pack_start(renderer, False)
            destination_object.add_attribute(renderer, "pixbuf", 2)
            
            renderer = Gtk.CellRendererText()
            destination_object.pack_start(renderer, False)
            destination_object.add_attribute(renderer, "text", 1)
        else:
            raise TypeError(
                    "Only expecting Gtk.ComboBox objects to want our model.")
        
    class ExcludeNameFilter:
        def __init__(self, avoid_name):
            self._avoid_name = avoid_name
        
        def matches(self, vm):
            return vm.name != self._avoid_name

