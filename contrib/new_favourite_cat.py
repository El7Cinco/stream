# encoding: utf-8
# api: streamtuner2
# title: New favourite category
# description: Introduces new bookmarks categories
# version: 0.3
# type: feature
# category: ui
# config: -
# priority: optional
# 
# Adds a "New favourite category..." under Station > Extensions menu.
#
#  · New categories will show up in the bookmarks channel under favourite.
#  · Also adds a "Bookmark to > …" context submenu.
#  · Still requires clicking/reloading the custom bookmark category.
#  · DND between bookmark categories is not supported.
#  · Subcategories can be removed (but requires exact name input).
#
# This is somewhat of a workaround. ST2 station lists are still unfit
# for bookmark management, because it wasn't a project goal as such.
#


from uikit import *
from config import *

# 
class new_favourite_cat (object):
    plugin = "new_favourite_cat"
    meta = plugin_meta()
    parent = None
    w = None

    # hook up menu entry
    def __init__(self, parent):
        self.parent = parent
        uikit.add_menu([parent.extensions], "New favourite category…", self.win, insert=3)
        self.create_submenu(parent)
        self.update_submenu()
  
    # show input window
    def win(self, *w):
        w = self.w = gtk.Dialog(
            'Bookmark category',
            self.parent.win_streamtuner2, 
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_DELETE, gtk.RESPONSE_DELETE_EVENT, gtk.STOCK_NEW, gtk.RESPONSE_APPLY)
        )
        input = gtk.Entry(35)
        w.vbox.pack_start(input)
        log.UI(w.vbox.get_children())
        w.show_all()
        self.add(self.w, w.run(), input.get_text())

    # add category
    def add(self, w, r, title):
        bm = self.parent.bookmarks
        have = bm.streams.has_key(title)
        w.destroy()
        if r == gtk.RESPONSE_APPLY:
            log.NEW(title)
            if not have:
                bm.streams[title] = []
        elif r == gtk.RESPONSE_DELETE_EVENT:
            if have:
                bm.streams.pop(title, None)
        else:
            log.ERR_UI("unknown action", r)
        self.update_submenu()
        bm.update_categories()
        bm.display_categories()

    # craft Menu and two MenuItem parents
    def create_submenu(self, parent):
        self.submenu = gtk.Menu()
        uikit.add_menu([parent.streammenu], insert=1, label="Bookmark to", stock=gtk.STOCK_INDENT, submenu=self.submenu)
        uikit.add_menu([parent.streamactions], insert=3, label="Add bookmark to", stock=gtk.STOCK_INDENT, submenu=self.submenu)

    # bookmark to > … submenu w/ custom categories
    def update_submenu(self):
        bmc = self.parent.bookmarks.categories
        # clean menu items
        for w in self.submenu.get_children():
            self.submenu.remove(w)
        # add fresh entries
        if len(bmc) >= 2 and type(bmc[1]) is list:
            for label in bmc[1]:
                uikit.add_menu([self.submenu], label, lambda w,target=label: self.parent.bookmark(w, target))
        self.submenu.show_all()
    
