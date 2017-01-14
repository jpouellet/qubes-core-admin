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
    def __init__(self, sourceName, targetName):
        self.testSourceName = sourceName
        self.testTargetName = targetName
        
        self.testCalledClose = False
        self.testCalledShow = False
        
        self.testClickedOk = False
        self.testClickedCancel = False
        
        TransferWindow.__init__(self, self.testSourceName, self.testTargetName)

    def _close(self):
        self.testCalledClose = True
        
    def _show(self):
        self.testCalledShow = True

    def _clickedOk(self, button):
        TransferWindow._clickedOk(self, button)
        self.testClickedOk = True
	    
    def _clickedCancel(self, button):
        TransferWindow._clickedCancel(self, button)
        self.testClickedCancel = True
       
    def test_hasLinkedTheFields(self):
        self.assertIsNotNone(self._transferWindow)
        self.assertIsNotNone(self._transferOkButton)
        self.assertIsNotNone(self._transferCancelButton)
        self.assertIsNotNone(self._transferDescriptionLabel)
        self.assertIsNotNone(self._transferComboBox)
    
    def test_isShowingSource(self):
        self.assertTrue(self.testSourceName in self._transferDescriptionLabel.get_text())
    
    def test_lifecycleOpenAndClose(self):
        self.assertFalse(self.testCalledClose)
        self.assertFalse(self.testCalledShow)        
        self.assertFalse(self.testClickedOk)
        self.assertFalse(self.testClickedCancel)
        
        try:
            self.confirmTransfer()
        except:
            pass
            
        self.assertFalse(self.testCalledClose)
        self.assertTrue(self.testCalledShow)
        self.assertFalse(self.testClickedOk)
        self.assertFalse(self.testClickedCancel)

        self._transferOkButton.clicked()
        
        self.assertTrue(self.testCalledClose)
        self.assertTrue(self.testClickedOk)
        self.assertFalse(self.testClickedCancel)
        
    
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
