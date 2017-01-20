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
from core.rpcconfirmation import *
from gtkhelpers import VMListModelerMock

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
