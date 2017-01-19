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

class RPCConfirmationWindowTestBase(RPCConfirmationWindow):
    def __init__(self, source_name, rpc_operation, target_name):
        self.test_source_name = source_name
        self.test_rpc_operation = rpc_operation
        self.test_target_name = target_name
        
        self.test_called_close = False
        self.test_called_show = False
        
        self.test_clicked_ok = False
        self.test_clicked_cancel = False
        
        RPCConfirmationWindow.__init__(self, 
                                        self.test_source_name, 
                                        self.test_rpc_operation,
                                        self.test_target_name)

    def _close(self):
        self.test_called_close = True
        
    def _show(self):
        self.test_called_show = True

    def _clicked_ok(self, button):
        RPCConfirmationWindow._clicked_ok(self, button)
        self.test_clicked_ok = True
	    
    def _clicked_cancel(self, button):
        RPCConfirmationWindow._clicked_cancel(self, button)
        self.test_clicked_cancel = True
       
    def test_has_linked_the_fields(self):
        self.assertIsNotNone(self._rpc_window)
        self.assertIsNotNone(self._rpc_ok_button)
        self.assertIsNotNone(self._rpc_cancel_button)
        self.assertIsNotNone(self._rpc_label)
        self.assertIsNotNone(self._source_entry)
        self.assertIsNotNone(self._rpc_combo_box)
        self.assertIsNotNone(self._error_bar)
        self.assertIsNotNone(self._error_message)
    
    def test_is_showing_source(self):
        self.assertTrue(self.test_source_name in 
                            self._source_entry.get_text())
    
    def test_is_showing_operation(self):
        self.assertTrue(self.test_rpc_operation in 
                            self._rpc_label.get_text())
    
    def test_hide_dom0_and_source(self):
        self._rpc_combo_box
    
    def test_lifecycle_open_select_ok(self):
        self._lifecycle_start(select_target = True)
        self._lifecycle_click(click_type = "ok")

    def test_lifecycle_open_select_cancel(self):
        self._lifecycle_start(select_target = True)
        self._lifecycle_click(click_type = "cancel")

    def test_lifecycle_open_select_exit(self):
        self._lifecycle_start(select_target = True)
        self._lifecycle_click(click_type = "exit")

    def test_lifecycle_open_cancel(self):
        self._lifecycle_start(select_target = False)
        self._lifecycle_click(click_type = "cancel")

    def test_lifecycle_open_exit(self):
        self._lifecycle_start(select_target = False)
        self._lifecycle_click(click_type = "exit")

    def _lifecycle_click(self, click_type):
        if click_type == "ok":
            self._rpc_ok_button.clicked()
            
            self.assertTrue(self.test_clicked_ok)
            self.assertFalse(self.test_clicked_cancel)
            self.assertTrue(self._confirmed)
            self.assertIsNotNone(self._target_qid)
            self.assertIsNotNone(self._target_name)
        elif click_type == "cancel":
            self._rpc_cancel_button.clicked()
            
            self.assertFalse(self.test_clicked_ok)
            self.assertTrue(self.test_clicked_cancel)
            self.assertFalse(self._confirmed)
        elif click_type == "exit":
            self._close()
            
            self.assertFalse(self.test_clicked_ok)
            self.assertFalse(self.test_clicked_cancel)
            self.assertIsNone(self._confirmed)
            
        self.assertTrue(self.test_called_close)
        
            
    def _lifecycle_start(self, select_target):
        self.assertFalse(self.test_called_close)
        self.assertFalse(self.test_called_show)        
        
        self.assert_initial_state()
                
        try:
            # We expect the call to exit immediately, since no window is opened 
            self._confirm_rpc()
        except:
            pass
            
        self.assertFalse(self.test_called_close)
        self.assertTrue(self.test_called_show)        
        
        self.assert_initial_state()
        
        if select_target:
            self._rpc_combo_box.set_active(1)
            
            self.assertTrue(self._rpc_ok_button.get_sensitive())
            
            self.assertIsNotNone(self._target_qid)
            self.assertIsNotNone(self._target_name)
            
        self.assertFalse(self.test_called_close)
        self.assertTrue(self.test_called_show)        
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        self.assertFalse(self._confirmed)
        
    def _new_VM_list_modeler(self):
        return VMListModelerMock()
    
class RPCConfirmationWindowTestNoTarget(RPCConfirmationWindowTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        RPCConfirmationWindowTestBase.__init__(self, 
                            "test-source", "test.Operation", None)
        
    def assert_initial_state(self):
        self.assertIsNone(self._target_qid)
        self.assertIsNone(self._target_name)
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        self.assertFalse(self._confirmed)
        self.assertFalse(self._rpc_ok_button.get_sensitive()) 
        self.assertFalse(self._error_bar.get_visible())
    
class RPCConfirmationWindowTestWithTarget(RPCConfirmationWindowTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        RPCConfirmationWindowTestBase.__init__(self, 
                            "test-source", "test.Operation", "test-target")
    
    def test_lifecycle_open_ok(self):
        self._lifecycle_start(select_target = False)
        self._lifecycle_click(click_type = "ok")
    
    def assert_initial_state(self):
        self.assertIsNotNone(self._target_qid)
        self.assertIsNotNone(self._target_name)
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        self.assertFalse(self._confirmed)
        self.assertTrue(self._rpc_ok_button.get_sensitive()) 
        
    def _lifecycle_click(self, click_type):
        RPCConfirmationWindowTestBase._lifecycle_click(self, click_type)
        self.assertIsNotNone(self._target_qid)
        self.assertIsNotNone(self._target_name)
            
class RPCConfirmationWindowTestWithTargetInvalid(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
    
    def test_unknown(self):
        self.assert_raises_error(True, "test-source", "test-wrong-target")
            
    def test_empty(self):
        self.assert_raises_error(True, "test-source", "")
    
    def test_equals_source(self):
        self.assert_raises_error(True, "test-source", "test-source")
            
    def assert_raises_error(self, expect, source, target):
        rpcWindow = RPCConfirmationWindowTestBase(source, 
                                                    "test.Operation", target)
        self.assertEquals(expect, rpcWindow._error_bar.get_visible())
            
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
        
class MockRPCConfirmationWindow(RPCConfirmationWindow):
    def _new_VM_list_modeler(self):
        return VMListModelerMock()
        
if __name__=='__main__':
    test = False
    window = False

    if len(sys.argv) == 1 or sys.argv[1] == '-t':
        test = True
    elif sys.argv[1] == '-w':
        window = True
    else:
        print "Usage: " + __file__ + " [-t|-w]"
    
    if window:
        print MockRPCConfirmationWindow(
                        "test-source", "qubes.Filecopy")._confirm_rpc()
    elif test:
        unittest.main(argv = [sys.argv[0]])
