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

import unittest
from core.gtkhelpers import *

class TransferWindowTestBase(TransferWindow):
    def __init__(self, source_name, target_name):
        self.test_source_name = source_name
        self.test_target_name = target_name
        
        self.test_called_close = False
        self.test_called_show = False
        
        self.test_clicked_ok = False
        self.test_clicked_cancel = False
        
        TransferWindow.__init__(self, self.test_source_name, 
                                    self.test_target_name)

    def _close(self):
        self.test_called_close = True
        
    def _show(self):
        self.test_called_show = True

    def _clicked_ok(self, button):
        TransferWindow._clicked_ok(self, button)
        self.test_clicked_ok = True
	    
    def _clicked_cancel(self, button):
        TransferWindow._clicked_cancel(self, button)
        self.test_clicked_cancel = True
       
    def test_has_linked_the_fields(self):
        self.assertIsNotNone(self._transfer_window)
        self.assertIsNotNone(self._transfer_ok_button)
        self.assertIsNotNone(self._transfer_cancel_button)
        self.assertIsNotNone(self._transfer_description_label)
        self.assertIsNotNone(self._transfer_combo_box)
    
    def test_is_showing_source(self):
        self.assertTrue(self.test_source_name in 
                            self._transfer_description_label.get_text())
    
    def test_lifecycle_open_and_close(self):
        self.assertFalse(self.test_called_close)
        self.assertFalse(self.test_called_show)        
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        
        try:
            self.confirm_transfer()
        except:
            pass
            
        self.assertFalse(self.test_called_close)
        self.assertTrue(self.test_called_show)        
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        
        self._transfer_ok_button.clicked()
        
        self.assertTrue(self.test_called_close)    
        self.assertTrue(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        
    def _new_VM_list_modeler(self):
        return VMListModelerMock()
    
class TransferWindowTestNoTarget(TransferWindowTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        TransferWindowTestBase.__init__(self, "test-source", None)
    
class TransferWindowTestWithTarget(TransferWindowTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        TransferWindowTestBase.__init__(self, "test-source", "test-target")
    
class VMListModelerMock(VMListModeler):
    def _load_list(self):
        self._list = [  QubesVmLabel(2, "red", "test-red1"),
                        QubesVmLabel(4, "red", "test-red2"),
                        QubesVmLabel(7, "red", "test-red3"),
                        QubesVmLabel(8, "green", "test-source"),
                        QubesVmLabel(10, "orange", "test-target"),
                        QubesVmLabel(15, "red", "test-disp6", True) ] 
        

class VMListModelerTest(VMListModelerMock, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        VMListModeler.__init__(self)
    
    def test_list_gets_loaded(self):
        self.assertIsNotNone(self._list)

    def test_apply_model(self):
        new_object = Gtk.ComboBox()
        self.assertIsNone(new_object.get_model())
        
        self.apply_model(new_object)
        
        self.assertIsNotNone(new_object.get_model())

    def test_apply_model_only_combobox(self):
        invalid_types = [ 1, "One", u'1', {'1': "one"}, VMListModeler()]
        
        for invalid_type in invalid_types:
            with self.assertRaises(TypeError):
                self.apply_model(invalid_type)
        
    def test_apply_model_exclusions(self):
        combo = Gtk.ComboBox()
        
        self.apply_model(combo)
        self.assertEquals(6, len(combo.get_model()))
        
        self.apply_model(combo, [   VMListModeler.ExcludeNameFilter(
                                        self._list[0].name) ])
        self.assertEquals(5, len(combo.get_model()))
        
        self.apply_model(combo, [   VMListModeler.ExcludeNameFilter(
                                        self._list[0].name), 
                                    VMListModeler.ExcludeNameFilter(
                                        self._list[1].name) ])
        self.assertEquals(4, len(combo.get_model()))
        
if __name__=='__main__':
    unittest.main()
