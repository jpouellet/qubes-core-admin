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
from core.rpcconfirmation import RPCConfirmationWindow
from gtkhelpers import VMListModelerMock, GtkTestCase, FocusStealingHelperMock

class MockRPCConfirmationWindow(RPCConfirmationWindow):
    def _new_VM_list_modeler(self):
        return VMListModelerMock()

    def _new_focus_stealing_helper(self):
        return FocusStealingHelperMock(
                    self._rpc_window,
                    self._rpc_ok_button,
                    self._focus_stealing_seconds)

    def __init__(self, source, rpc_operation, target = None,
                    focus_stealing_seconds = 1):
        self._focus_stealing_seconds = focus_stealing_seconds

        RPCConfirmationWindow.__init__(self, source, rpc_operation, target)

    def is_error_visible(self):
        return self._error_bar.get_visible()

class RPCConfirmationWindowTestBase(MockRPCConfirmationWindow, GtkTestCase):
    def __init__(self, test_method, source_name = "test-source",
                 rpc_operation = "test.Operation", target_name = None):
        GtkTestCase.__init__(self, test_method)
        self.test_source_name = source_name
        self.test_rpc_operation = rpc_operation
        self.test_target_name = target_name

        self._test_time = 0.1

        self.test_called_close = False
        self.test_called_show = False

        self.test_clicked_ok = False
        self.test_clicked_cancel = False

        MockRPCConfirmationWindow.__init__(self,
                                       self.test_source_name,
                                       self.test_rpc_operation,
                                       self.test_target_name,
                                       focus_stealing_seconds = self._test_time)

    def _can_perform_action(self):
        return True

    def _close(self):
        self.test_called_close = True

    def _show(self):
        self.test_called_show = True

    def _clicked_ok(self, button):
        MockRPCConfirmationWindow._clicked_ok(self, button)
        self.test_clicked_ok = True

    def _clicked_cancel(self, button):
        MockRPCConfirmationWindow._clicked_cancel(self, button)
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

    def test_format_rpc_text(self):
        self.assertEquals("qubes.<b>Test</b>",
                            self._format_rpc_text("qubes.Test"))
        self.assertEquals("custom.<b>Domain</b>",
                            self._format_rpc_text("custom.Domain"))
        self.assertEquals("nodomain",
                            self._format_rpc_text("nodomain"))
        self.assertEquals("domain.<b>Sub.Operation</b>",
                            self._format_rpc_text("domain.Sub.Operation"))
        self.assertEquals("",
                            self._format_rpc_text(""))
        self.assertEquals(".",
                            self._format_rpc_text("."))

    def test_hide_dom0_and_source(self):
        model = self._rpc_combo_box.get_model()

        self.assertIsNotNone(model)

        model_iter = model.get_iter_first()
        found_dom0 = False
        found_source = False

        while model_iter != None:
            domain_name = model.get_value(model_iter, 1)

            if domain_name == 'dom0':
                found_dom0 = True
            elif domain_name == self.test_source_name:
                found_source = True

            model_iter = model.iter_next(model_iter)


        self.assertFalse(found_dom0)
        self.assertFalse(found_source)

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

        self.assert_initial_state(False)
        self.assertTrue(isinstance(self._focus_helper, FocusStealingHelperMock))

        # Need the following because of pylint's complaints
        if isinstance(self._focus_helper, FocusStealingHelperMock):
            FocusStealingHelperMock.simulate_focus(self._focus_helper)

        self.flush_gtk_events(self._test_time*2)
        self.assert_initial_state(True)

        try:
            # We expect the call to exit immediately, since no window is opened
            self.confirm_rpc()
        except BaseException:
            pass

        self.assertFalse(self.test_called_close)
        self.assertTrue(self.test_called_show)

        self.assert_initial_state(True)

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

    def assert_initial_state(self, after_focus_timer):
        self.assertIsNone(self._target_qid)
        self.assertIsNone(self._target_name)
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        self.assertFalse(self._confirmed)
        self.assertFalse(self._rpc_ok_button.get_sensitive())
        self.assertFalse(self._error_bar.get_visible())

        if after_focus_timer:
            self.assertTrue(self._focus_helper.can_perform_action())
        else:
            self.assertFalse(self._focus_helper.can_perform_action())

class RPCConfirmationWindowTestWithTarget(RPCConfirmationWindowTestBase):
    def __init__(self, test_method):
        RPCConfirmationWindowTestBase.__init__(self, test_method,
                 source_name = "test-source", rpc_operation = "test.Operation",
                 target_name =  "test-target")

    def test_lifecycle_open_ok(self):
        self._lifecycle_start(select_target = False)
        self._lifecycle_click(click_type = "ok")

    def assert_initial_state(self, after_focus_timer):
        self.assertIsNotNone(self._target_qid)
        self.assertIsNotNone(self._target_name)
        self.assertFalse(self.test_clicked_ok)
        self.assertFalse(self.test_clicked_cancel)
        self.assertFalse(self._confirmed)
        if after_focus_timer:
            self.assertTrue(self._rpc_ok_button.get_sensitive())
            self.assertTrue(self._focus_helper.can_perform_action())
        else:
            self.assertFalse(self._rpc_ok_button.get_sensitive())
            self.assertFalse(self._focus_helper.can_perform_action())

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
        rpcWindow = MockRPCConfirmationWindow(source, "test.Operation", target)
        self.assertEquals(expect, rpcWindow.is_error_visible())

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
        print MockRPCConfirmationWindow("test-source",
                                        "qubes.Filecopy",
                                        "test-red1").confirm_rpc()
    elif test:
        unittest.main(argv = [sys.argv[0]])
