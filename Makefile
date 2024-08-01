# Requires 
# · http://fossil.include-once.org/versionnum/
# · http://fossil.include-once.org/xpm/

SHELL   := /bin/bash #(for brace expansion)
NAME    := streamtuner2
VERSION := $(shell version get:plugin st2.py || echo 2.2dev)
DEST    := /usr/share/streamtuner2
DOCS    := /usr/share/doc/streamtuner2
INST    := install -m 644
PACK    := xpm
DEPS    := -n $(NAME) -d "python|python3" -d "python-pyquery|python3-pyquery" -d "python-gtk2|python3-gi" -d "python-requests|python3-requests"
DEPS_A  := -n $(NAME) -d pygtk -d python2 -d python2-cssselect -d python2-keybinder2 -d python2-lxml -d python2-pillow -d python2-pyquery -d python2-xdg -d python2-requests --provides streamtuner-python
OPTS    := -s src -u packfile,fixperms -f --prefix=$(DEST) --deb-compression=xz --rpm-compression=xz --exe-autoextract

# targets
.PHONY:	bin
all:	gtk3 #(most used)
pack:	all ver docs xpm src
gtk3:	gtk3.xml.gz
zip:	pyz
print-%:
	@echo $*=$($*)


# Convert between internal GtkBuilder-gzipped file and uncompressed xml
gtk3.xml.gz: gtk3.xml
	gzip -c9 < gtk3.xml > gtk3.xml.gz
glade:
	gzip -dc > gtk3.xml < gtk3.xml.gz
	glade gtk3.xml 2>/dev/null
	gzip -c9 < gtk3.xml > gtk3.xml.gz

# Prepare packaging
docs:
ver:	# copy `version:` info
	version get:plugin st2.py write:control PKG-INFO
clean:
	rm *.pyc */*.pyc
	rm -r __pycache__ */__pycache__

#-- bundles
xpm: deb pyz tar rpm exe
deb:
	$(PACK) -t $@ $(OPTS) $(DEPS) -p "$(NAME)-VERSION.deb" st2.py
rpm:
	$(PACK) -t $@ $(OPTS) $(DEPS) -p "$(NAME)-VERSION.rpm" st2.py
tar:
	$(PACK) -t $@ $(OPTS) $(DEPS) -p "$(NAME)-VERSION.bin.txz" st2.py
exe:
	$(PACK) -t $@ $(OPTS) $(DEPS) -p "$(NAME)-VERSION.exe" \
	--exe-exec 'usr\share\streamtuner2\dev\install_python_gtk.bat' \
	--exe-dest c:/ --version $(VERSION) .win.pack st2.py
arch:
	$(PACK) -t $@ $(OPTS) $(DEPS_A) -p "$(NAME)-VERSION.arch.txz" st2.py
osxpkg:
	$(PACK) -t $@ $(OPTS) $(DEPS_A) -p "$(NAME)-VERSION.osxz" st2.py
pyz:
        #@BUG: relative package references leave a /tmp/doc/ folder
	$(PACK) -u packfile -s src -t zip --zip-shebang "/usr/bin/env python"	\
		-f -p "$(NAME)-$(VERSION).pyz" --prefix=./  .zip.py st2.py
src:
	cd .. && pax -wvJf streamtuner2/streamtuner2-$(VERSION).src.txz \
		streamtuner2/*.{py,png,desktop} streamtuner2/channels/*.{py,png} \
		streamtuner2/{bundle/,contrib/,help/,gtk3.xml.gz,NEWS,READ,PACK,PKG,CRED,Make,bin,.zip}*

snap:	pyz
	cp streamtuner2-*.pyz streamtuner2.pyz
	zip snapcraft.zip streamtuner2.pyz
	version read ./st2.py write:_raw_ dev/snapcraft.yaml
	snapcraft 

# test .deb contents
check:
	dpkg-deb -c streamtuner2*deb
	dpkg-deb -I streamtuner2*deb
	rpm -qpil *rpm
	
upload:
	scp *.{deb,rpm,exe,pyz,arch.txz,txz} io:st2/
	scp *.{deb,rpm,exe,pyz,arch.txz,txz} sf:/home/frs/project/streamtuner2/

# manual installation
install:
	mkdir	-p			$(DEST)/channels
	mkdir	-p			$(DOCS)/streamtuner2/help/img
	install -m 755	bin		/usr/bin/streamtuner2
	$(INST)		*py		-t $(DEST)
	$(INST)		gtk3*		-t $(DEST)
	$(INST)		channels/*py	-t $(DEST)/channels
	$(INST)		help/*page	-t $(DOCS)/streamtuner2/help
	$(INST)		help/img/*	-t $(DOCS)/streamtuner2/help/img
	$(INST)		CREDITS		-t $(DEST)
	$(INST)		README		-t $(DOCS)
	$(INST)		*.desktop	-t /usr/share/applications/
	$(INST)		icon.png	/usr/share/pixmaps/streamtuner2.png
	$(INST)		help/str*2.1	-t /usr/share/man/man1/
	pip install requests pyquery lxml pillow xdg keybinder

# start locally
st2: run
run:
	#MALLOC_CHECK_=2 PYTHONVERBOSE=2
	python -B  ./st2.py -D  -e dev_faulthandler

yelp:
	yelp help/index.page 2>/dev/null &
	(cd help/html ; yelp-build html ..)

chm:
	cd help         # mallard → epub → docbook → chm
	yelp-build epub
	mv index.epub help.epub
	pandoc help.epub -t docbook > help.docbook
	rm help.epub
	#lxy...?
