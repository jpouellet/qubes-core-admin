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
        
        TransferWindow.__init__(self, self.test_source_name, self.test_target_name)

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
    
    def test_isShowingSource(self):
        self.assertTrue(self.test_source_name in self._transfer_description_label.get_text())
    
    def test_lifecycleOpenAndClose(self):
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
        
    
class TransferWindowTestNoTarget(TransferWindowTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        TransferWindowTestBase.__init__(self, "test-source", None)
    
class TransferWindowTestWithTarget(TransferWindowTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        TransferWindowTestBase.__init__(self, "test-source", "test-target")
    
if __name__=='__main__':
    unittest.main()
