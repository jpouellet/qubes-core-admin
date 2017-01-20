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

import unittest, sys
from core.gtkhelpers import *
            
class VMListModelerMock(VMListModeler):
    def _load_list(self):
        self._list = [  MockVm(0, "dom0", "black"),
                        MockVm(2, "test-red1", "red"),
                        MockVm(4, "test-red2", "red"),
                        MockVm(7, "test-red3", "red"),
                        MockVm(8, "test-source", "green"),
                        MockVm(10, "test-target", "orange"),
                        MockVm(15, "test-disp6", "red", True) ] 
   
class MockVmLabel:
    def __init__(self, index, color, name, dispvm = False):
        self.index = index
        self.color = color
        self.name = name
        self.dispvm = dispvm
        self.icon = "gnome-foot" 
        
class MockVm:
    def __init__(self, qid, name, color, dispvm = False):
        self.qid = qid
        self.name = name
        self.label = MockVmLabel(qid, 0x000000, color, dispvm)

class MockComboEntry:
    def __init__(self, text):
        self._text = text
        
    def get_active_id(self):
        return self._text

    def get_text(self):
        return self._text
        
class VMListModelerTest(VMListModelerMock, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        VMListModeler.__init__(self)
    
    def test_list_gets_loaded(self):
        self.assertIsNotNone(self._list)

    def test_valid_qube_name(self):
        self.apply_model(Gtk.ComboBox())
    
        for name in [ "test-red1", "test-red2", "test-red3", 
                      "test-target", "test-disp6" ]:
                      
            mock = MockComboEntry(name)
            self.assertEquals(name, self._get_valid_qube_name(mock, mock, []))
            self.assertEquals(name, self._get_valid_qube_name(None, mock, []))
            self.assertEquals(name, self._get_valid_qube_name(mock, None, []))
            self.assertIsNone(self._get_valid_qube_name(None, None, []))

    def test_valid_qube_name_exceptions(self):
        list_exc = ["test-disp6", "test-red2"]
    
        self.apply_model(Gtk.ComboBox(), 
            [VMListModeler.ExcludeNameFilter(list_exc[0], list_exc[1])])
    
        for name in list_exc:
            mock = MockComboEntry(name)
            self.assertIsNone(self._get_valid_qube_name(mock, mock, list_exc))
            self.assertIsNone(self._get_valid_qube_name(None, mock, list_exc))
            self.assertIsNone(self._get_valid_qube_name(mock, None, list_exc))

    def test_invalid_qube_name(self):
        self.apply_model(Gtk.ComboBox())
    
        for name in [ "test-nonexistant", None, "", 1 ]:
                      
            mock = MockComboEntry(name)
            self.assertIsNone(self._get_valid_qube_name(mock, mock, []))
            self.assertIsNone(self._get_valid_qube_name(None, mock, []))
            self.assertIsNone(self._get_valid_qube_name(mock, None, []))

    def test_apply_model(self):
        new_object = Gtk.ComboBox()
        self.assertIsNone(new_object.get_model())
        
        self.apply_model(new_object)
        
        self.assertIsNotNone(new_object.get_model())

    def test_apply_model_with_entry(self):
        new_object = Gtk.ComboBox.new_with_entry()
        
        self.assertIsNone(new_object.get_model())
        
        self.apply_model(new_object)
        
        self.assertIsNotNone(new_object.get_model())

    def test_apply_model_only_combobox(self):
        invalid_types = [ 1, "One", u'1', {'1': "one"}, VMListModelerMock()]
        
        for invalid_type in invalid_types:
            with self.assertRaises(TypeError):
                self.apply_model(invalid_type)
        
    def test_apply_model_exclusions(self):
        combo = Gtk.ComboBox()
        
        self.apply_model(combo)
        self.assertEquals(7, len(combo.get_model()))
        
        self.apply_model(combo, [   VMListModeler.ExcludeNameFilter(
                                        self._list[0].name) ])
        self.assertEquals(6, len(combo.get_model()))
        
        self.apply_model(combo, [   VMListModeler.ExcludeNameFilter(
                                        self._list[0].name), 
                                    VMListModeler.ExcludeNameFilter(
                                        self._list[1].name) ])
        self.assertEquals(5, len(combo.get_model()))
        
    def test_apply_icon(self):
        new_object = Gtk.Entry()
        
        self.assertIsNone(
                new_object.get_icon_pixbuf(Gtk.EntryIconPosition.PRIMARY))
                
        self.apply_icon(new_object, "test-disp6")
        
        self.assertIsNotNone(
                new_object.get_icon_pixbuf(Gtk.EntryIconPosition.PRIMARY))

    def test_apply_icon_only_entry(self):
        invalid_types = [ 1, "One", u'1', {'1': "one"}, Gtk.ComboBox()]
        
        for invalid_type in invalid_types:
            with self.assertRaises(TypeError):
                self.apply_icon(invalid_type, "test-disp6")
        
    def test_apply_icon_only_entry(self):
        new_object = Gtk.Entry()
        
        for name in [ "test-red1", "test-red2", "test-red3", 
                      "test-target", "test-disp6" ]:
            self.apply_icon(new_object, name)
        
        for name in [ "test-nonexistant", None, "", 1 ]:
            with self.assertRaises(ValueError):
                self.apply_icon(new_object, name)
        
if __name__=='__main__':
    unittest.main()
