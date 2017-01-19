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
                  'source': "sourceEntry", 
                  'rpc_label' : "rpcLabel",
                  'target': "TargetCombo",
                  'error_bar': "ErrorBar",
                  'error_message': "ErrorMessage",
                }

    def _clicked_ok(self, button):
        self._confirmed = True
        self._close()
	    
    def _clicked_cancel(self, button):
        self._confirmed = False
        self._close()

    def _update_ok_button_sensitivity(self, data):
        valid = (data != None)
        
        if valid:
            (self._target_qid, self._target_name) = data
        else:
            self._target_qid = None
            self._target_name = None

        self._rpc_ok_button.set_sensitive(valid)

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
        self._rpc_label = self._gtk_builder.get_object(
                                            self._source_id['rpc_label'])
        self._source_entry = self._gtk_builder.get_object(
                                            self._source_id['source'])
        self._rpc_combo_box = self._gtk_builder.get_object(
                                            self._source_id['target'])
        self._error_bar = self._gtk_builder.get_object(
                                            self._source_id['error_bar'])
        self._error_message = self._gtk_builder.get_object(
                                            self._source_id['error_message'])
        
        rpc_text  = rpc_operation[0:rpc_operation.find('.')+1] + "<b>"
        rpc_text += rpc_operation[rpc_operation.find('.')+1:len(rpc_operation)] 
        rpc_text += "</b>"
        
        self._rpc_label.set_markup(rpc_text)

        self._rpc_ok_button.connect("clicked", self._clicked_ok)
        self._rpc_cancel_button.connect("clicked", self._clicked_cancel)
        
        self._error_bar.connect("response", self._close_error)
        
        list_modeler = self._new_VM_list_modeler()
        
        list_modeler.apply_model(self._rpc_combo_box, 
                    [ VMListModeler.ExcludeNameFilter("dom0"),
                      VMListModeler.ExcludeNameFilter(source) ],
                    selection_trigger = self._update_ok_button_sensitivity,
                    activation_trigger = self._clicked_ok )
                    
        self._source_entry.set_text(source)
        list_modeler.apply_icon(self._source_entry, source)
        
        self._confirmed = None

        self._set_initial_target(source, target)
        
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
            return {    'target_name': self._target_name,
                        'target_qid': self._target_qid
                   }
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
        self._icon_getter = GtkIconGetter(32)
        self._load_list()
        self._create_entries()
        
                  
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
        
    def _create_entries(self):
        self._entries = {}
        
        for vm in self._list:
            icon = self._get_icon(vm)
                
            self._entries[vm.name] = {  'qid': vm.qid,
                                        'icon': icon }
                    
                    
    def _get_valid_qube_name(self, combo, entry_box, exclusions):
        name = None
        
        if combo and combo.get_active_id():
            selected = combo.get_active_id()
            
            if selected in self._entries and selected not in exclusions:
                name = selected
        
        if not name and entry_box:
            typed = entry_box.get_text()
        
            if typed in self._entries and typed not in exclusions:
                name = typed
            
        return name
        
    def _combo_change(self, selection_trigger, combo, entry_box, exclusions):
        data = None
        name = self._get_valid_qube_name(combo, entry_box, exclusions)
        
        if name:
            entry = self._entries[name]
            
            data = (entry['qid'], name)
        
            if entry_box:
                entry_box.set_icon_from_pixbuf(
                    Gtk.EntryIconPosition.PRIMARY, entry['icon'])
        else:
            if entry_box:
                entry_box.set_icon_from_stock(
                    Gtk.EntryIconPosition.PRIMARY, "gtk-find")
               
        if selection_trigger:
            selection_trigger(data)
        
    def _entry_activate(self, activation_trigger, combo, entry_box, exclusions):
        name = self._get_valid_qube_name(combo, entry_box, exclusions)
        
        if name:
            activation_trigger(entry_box)
        
    def apply_model(self, destination_object, vm_filter_list = [], 
                    selection_trigger = None, activation_trigger = None ):
        if isinstance(destination_object, Gtk.ComboBox):
            list_store = Gtk.ListStore(int, str, GdkPixbuf.Pixbuf)

            exclusions = []
            for vm in self._list:
                matches = True
                
                for vm_filter in vm_filter_list:
                    if not vm_filter.matches(vm):
                        matches = False
                        break
                
                if matches:
                    entry = self._entries[vm.name]

                    list_store.append([entry['qid'], vm.name, entry['icon']])
                else:
                    exclusions += [vm.name]

            destination_object.set_model(list_store)
            destination_object.set_id_column(1)

            if destination_object.get_has_entry():
                entry_box = destination_object.get_child()
            
                completion = Gtk.EntryCompletion()
                completion.set_inline_selection(True)
                completion.set_inline_completion(True)
                completion.set_popup_completion(False)
                completion.set_model(list_store)
                completion.set_text_column(1)
                
                entry_box.set_completion(completion)
                if activation_trigger:
                    entry_box.connect("activate", 
                        lambda entry: self._entry_activate(
                            activation_trigger, 
                            destination_object, 
                            entry, 
                            exclusions))
                
                # Removes the extra text column created b/c of the entry, 
                # but unfortunately generates a GTK assertion error in console
                destination_object.clear()
            else:
                entry_box = None
            
            renderer = Gtk.CellRendererPixbuf() 
            destination_object.pack_start(renderer, False)
            destination_object.add_attribute(renderer, "pixbuf", 2)
            destination_object.set_entry_text_column(1)
            
            renderer = Gtk.CellRendererText()
            destination_object.pack_start(renderer, False)
            destination_object.add_attribute(renderer, "text", 1)
            
            changed_function = lambda combo: self._combo_change(
                             selection_trigger, 
                             combo, 
                             entry_box,
                             exclusions)
                             
            destination_object.connect("changed", changed_function)
            changed_function(destination_object)
            
        else:
            raise TypeError(
                    "Only expecting Gtk.ComboBox objects to want our model.")
    
    def apply_icon(self, entry, qube_name):
        if isinstance(entry, Gtk.Entry):
            if qube_name in self._entries:
                entry.set_icon_from_pixbuf(
                        Gtk.EntryIconPosition.PRIMARY, 
                        self._entries[qube_name]['icon'])
            else:
                raise ValueError("The specified source qube does not exist!")
        else:
            raise TypeError(
                    "Only expecting Gtk.Entry objects to want our icon.")
                    
    class ExcludeNameFilter:
        def __init__(self, *avoid_names):
            self._avoid_names = avoid_names
        
        def matches(self, vm):
            return vm.name not in self._avoid_names

