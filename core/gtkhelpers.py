import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GdkPixbuf

class TransferWindow():
    _sourceFile = "gtk/TransferWindow.glade"
    _sourceId = {
        'window': "TransferWindow", 'ok': "okButton", 'cancel': "cancelButton", 'description': "TransferDescription", 'target': "TargetCombo"
    }
    _textDescription = "Allow domain '<b>%s</b>' to execute a file transfer?\n<small>Select the target domain and confirm with 'OK'.</small>"

    def _clickedOk(self, button):
        self.confirmed = True
        self.close()
	    
    def _clickedCancel(self, button):
        self.close()

    def __init__(self, source, target = None):
        self._gtkBuilder = Gtk.Builder()
        self._gtkBuilder.add_from_file(self._sourceFile)
        self._transferWindow = self._gtkBuilder.get_object(self._sourceId['window'])
        self._transferOkButton = self._gtkBuilder.get_object(self._sourceId['ok'])
        self._transferCancelButton = self._gtkBuilder.get_object(self._sourceId['cancel'])
        self._transferDescriptionLabel = self._gtkBuilder.get_object(self._sourceId['description'])
        self._transferComboBox = self._gtkBuilder.get_object(self._sourceId['target'])
        
        self._transferDescriptionLabel.set_markup(self._textDescription % source)
        
        self._transferOkButton.connect("clicked", self._clickedOk)
        self._transferCancelButton.connect("clicked", self._clickedCancel)
        self.confirmed = False
        self.targetId = None
        self.targetName = None
		
        self._transferOkButton.set_sensitive(True)
		
    def close(self):
        self._transferWindow.close()
		
    def show(self):
        self._transferWindow.connect("delete-event", Gtk.main_quit)
        self._transferWindow.show_all()
		
        Gtk.main()


def confirmTransfer():
    transferWindow = TransferWindow("test")
    transferWindow.show()
    
    if transferWindow.confirmed:
        return { 'targetId': transferWindow.targetId, 'targetName': transferWindow.targetName }
    else:
        return False

print(confirmTransfer())
