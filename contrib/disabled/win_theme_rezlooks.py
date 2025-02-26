# api: streamtuner2
# title: Default Windows theme
# description: Use "Rezlooks-dark" as default theme on Windows for SFX/EXE installer
# type: feature
# category: ui
# priority: optional
# pack: win_theme_rezlooks.py=../channels/
# depends: librezlooks.dll
# version: -1
# author: Doug Whiteley
# license: GNU GPL
#
# Sets a dark Gtk theme on Windows per default. To disable, simply
# uncheck this plugin. The standard rendering will take hold after
# a restart.
# Other themes can be used with the `gtk_theme` plugin easily.
#
# (!) Only works with `librezlooks.dll` in place however.


import os, shutil
from config import *
from uikit import gtk
from compat2and3 import *



# register a key
class win_theme_rezlooks(object):

    # plugin info
    module = "win_theme_rezlooks"
    meta = plugin_meta()
    gtk_dll = 'C:\\Python27\\Lib\\site-packages\\gtk-2.0\\runtime\\lib\\gtk-2.0\\2.10.0\\engines\\librezlooks.dll'
    gtk_dll_src = '%s/dev/librezlooks.dll' % conf.share

    # use builtin .GTKRC
    def __init__(self, parent):
        # assert gtk-engine is there, else copy it over
        if not os.path.exists(self.gtk_dll):
            if os.path.exists(self.gtk_dll_src):
                try:
                    shutil.copyfile(self.gtk_dll_src, self.gtk_dll)
                except:
                    log.ERR("could not copy librezlooks.dll")
                    return
            else:
                return
        # apply theme
        gtk.rc_parse_string(self.gtkrc)
        gtk.rc_reparse_all()
        # probably redundant:
        gtk.rc_reset_styles(gtk.settings_get_for_screen(gtk.gdk.screen_get_default()))
        parent.win_streamtuner2.queue_draw()

    # theme settings
    gtkrc = """
style "rezlooks-default"
{
  GtkButton::default_border = { 0, 0, 0, 0 }
  GtkButton::default_outside_border = { 0, 0, 0, 0 }
  GtkRange::trough_border = 0

  GtkWidget::focus_padding = 1

  GtkPaned::handle_size = 6

  GtkRange::slider_width = 15
  GtkRange::stepper_size = 15 # toolbar arrows
  GtkScrollbar::min_slider_length = 30
  GtkCheckButton::indicator_size = 12
  GtkMenuBar::internal-padding = 0

  GtkTreeView::expander_size = 14
  GtkExpander::expander_size = 16

  xthickness = 1
  ythickness = 1

  fg[NORMAL]        = "#cccccc" # very dark brown
  fg[PRELIGHT]      = "#cccccc" # text on buttons (hover)
  fg[ACTIVE]        = "#cccccc" # text on unfocused tabs
  fg[SELECTED]      = "#cccccc" # selected text on lists
  fg[INSENSITIVE]   = "#999999" # greyed "unused" text

  bg[NORMAL]		= "#202020" # entire background
  bg[PRELIGHT]		= "#181818" # button prelights
  bg[ACTIVE]		= "#282828" # selected taskbar items
  bg[SELECTED]		= "#333333" # ???
  bg[INSENSITIVE]	= "#424242" # greyed buttons

  base[NORMAL]		= "#080808" # window background
  base[PRELIGHT]	= "#3d3e3f" # menubar outline colour
  base[ACTIVE]		= "#282828" # selected item background (out of focus)
  base[SELECTED]	= "#333333" # selected hilight,tab/slider background, & menu stripe
  base[INSENSITIVE]	= "#282828" # greyed sliders

  text[NORMAL]		= "#cccccc" # text in general
  text[PRELIGHT]	= "#cccccc" # hover text (on buttons)
  text[ACTIVE]		= "#a2a2a2" # greyed text out of use (on highlight)
  text[SELECTED]	= "#eeeeee" # selected text (on highlight)
  text[INSENSITIVE]	= "#b1b1b1" # greyed text

  engine "rezlooks" 
  {
	scrollbar_color   = "#202020"
    menubarstyle      = 1       # 0 = flat, 1 = gradient
    menuitemstyle     = 1       # currently IGNORED
    listviewitemstyle = 1       # currently IGNORED
    progressbarstyle  = 1       # currently IGNORED
	animation         = TRUE
  }
}

style "rezlooks-progressbar" = "rezlooks-default"
{
  fg[PRELIGHT] = "#202020"
  xthickness = 1
  ythickness = 1

}

style "rezlooks-wide" = "rezlooks-default"
{
  xthickness = 2
  ythickness = 2
}

style "rezlooks-button" = "rezlooks-default"
{
  xthickness = 3
  ythickness = 3
  bg[NORMAL] = "#202020"
}

style "rezlooks-notebook" = "rezlooks-wide"
{
  bg[NORMAL] = "#202020" # inner window background colour
  bg[ACTIVE] = "#333333" # out of focus tabs
}


style "rezlooks-tasklist" = "rezlooks-default"
{
  xthickness = 5
  ythickness = 3
}

style "rezlooks-menu" = "rezlooks-default"
{
  xthickness = 2
  ythickness = 1
}

style "rezlooks-menu-item" = "rezlooks-default"
{
  xthickness = 2
  ythickness = 3
  fg[PRELIGHT] = "#cccccc"
  text[PRELIGHT] = "#cccccc"
}

style "rezlooks-menubar" = "rezlooks-default"
{
	fg[NORMAL] = "#cccccc"
	text[NORMAL] = "#cccccc"
	fg[PRELIGHT] = "#cccccc"
	fg[ACTIVE] = "#cccccc"
}

style "rezlooks-tree" = "rezlooks-default"
{
  xthickness = 2
  ythickness = 2
}

style "evolution-hack" = "rezlooks-default"
{
}

style "rezlooks-frame-title" = "rezlooks-default"
{
  fg[NORMAL] = "#404040"
}

style "rezlooks-panel" = "rezlooks-default"
{
  xthickness = 3
  ythickness = 3
}

style "rezlooks-tooltips" = "rezlooks-default"
{
  xthickness = 4
  ythickness = 4
  bg[NORMAL] = { 1.0,1.0,0.75 }
}

style "rezlooks-combo" = "rezlooks-default"
{
  xthickness = 1
  ythickness = 2
}

style "metacity-frame"
{
  # Normal base color
  #bg[NORMAL]  = "#bbbbbb"

  # Unfocused title background color
  #bg[INSENSITIVE]  = { 0.8, 0.8, 0.8 }

  # Unfocused title text color
  #fg[INSENSITIVE]  = { 1.55, 1.55, 1.55 }

  # Focused icon color
  #fg[NORMAL]  = { 0.2, 0.2, 0.2 }

  # Focused title background color
  bg[SELECTED]  = "#4d4e50"

  # Focused title text color
  fg[SELECTED]  = "#ffffff"
}

# widget styles
class "GtkWidget" style "rezlooks-default"
class "GtkButton" style "rezlooks-button"
class "GtkCombo"  style "rezlooks-button"
class "GtkRange"  style "rezlooks-wide"
class "GtkFrame"  style "rezlooks-wide"
class "GtkMenu"   style "rezlooks-menu"
class "GtkEntry"  style "rezlooks-button"
class "GtkMenuItem"    style "rezlooks-menu-item"
class "GtkStatusbar"   style "rezlooks-wide"
class "GtkNotebook"    style "rezlooks-notebook"
class "GtkProgressBar" style "rezlooks-progressbar"
class "*MenuBar*"      style "rezlooks-menubar"

class "MetaFrames" style "metacity-frame"
widget_class "*MenuItem.*" style "rezlooks-menu-item"

# combobox stuff
widget_class "*.GtkComboBox.GtkButton" style "rezlooks-combo"
widget_class "*.GtkCombo.GtkButton"    style "rezlooks-combo"

# tooltips stuff
widget_class "*.tooltips.*.GtkToggleButton" style "rezlooks-tasklist"
widget "gtk-tooltips" style "rezlooks-tooltips"

# treeview stuff
widget_class "*.GtkTreeView.GtkButton" style "rezlooks-tree"
widget_class "*.GtkCTree.GtkButton" style "rezlooks-tree"
widget_class "*.GtkList.GtkButton" style "rezlooks-tree"
widget_class "*.GtkCList.GtkButton" style "rezlooks-tree"
widget_class "*.GtkFrame.GtkLabel" style "rezlooks-frame-title"

# notebook stuff
widget_class "*.GtkNotebook.*.GtkEventBox" style "rezlooks-notebook"
widget_class "*.GtkNotebook.*.GtkViewport" style "rezlooks-notebook"

# evolution
widget_class "*GtkCTree*" style "evolution-hack"
widget_class "*GtkList*" style "evolution-hack"
widget_class "*GtkCList*" style "evolution-hack"
widget_class "*.ETree.*" style "evolution-hack"

"""
