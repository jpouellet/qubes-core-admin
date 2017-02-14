GLADE_PATH = $(PYTHON_SITEPATH)/qubes/glade

install:
ifndef PYTHON_SITEPATH
	$(error PYTHON_SITEPATH not defined)
endif
	mkdir -p $(DESTDIR)$(GLADE_PATH)
	cp RPCConfirmationWindow.glade $(DESTDIR)$(GLADE_PATH)
