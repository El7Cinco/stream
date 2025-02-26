# type: doc
# pack: README=/usr/share/doc/streamtuner2/


Streamtuner2
============

ST2 is a browser for internet radio/streaming stations. It queries
directories like Shoutcast, TuneIn, Xiph.org. SurfMusic, Jamendo etc.
for music/video streams/collections.

It mimics the original streamtuner 1 to some extend.
However it's written in Python now instead of C.


Installation howto
------------------

If possible, prefer the package directly from your BSD/Linux distribution
over manually installing dependencies.
The PYZ package is the easiest option for local installations.


Dependencies
------------

Running streamtuner2 requires Python and Gtk packages. Which nowadays are
installed per default. There's a few more Python packages required though:

 · python | python3
 · pygtk | python-gi
 · python-requests
 · python-pyquery
 · python-lxml
 · python-imaging | pillow
 · python-keybinder (optional)
 · python-xdg (optional)

Use your distro package manager with e.g.:

  sudo apt-get install python python-gtk2 python-xdg python-requests ...

Or utilize Pythons local package installer even:

  sudo pip install requests pyquery pillow


DEB / RPM
---------

There are rudimentary packages built as .DEB and .RPM version. Install
those if feasible. The dependencies may not match with your package
manager, and are somewhat incomplete. (See "Dependencies" section.)


PYZ
---

Other users may wish to try the new Python archive (.PYZ) instead. Which
requires little installation and can be run as is:

    python streamtuner2.pyz

You could even make this Python ZIP executable, and copy it in your PATH.


EXE
---

The Windows SFX package can meanwhile post-install Python and Gtk. It's
well-tested and even comes with an uninstaller.
The default path of "C:/" would create a standard Linux-esque C:/usr/bin
directory structure.  But the package is relocatable, so allows to be
unpacked even under "c:\program files\st2\" or else.


Manual installation
-------------------

If you've checked out the source code repository, or did download the
*.src.txz archive, then you can just run it right there:

   ./st2.py

The easy way:

  · Run `sudo make install`
    which installs into the default location (/usr/share/streamtuner2).

To install it manually:

  · Create a /usr/share/streamtuner2/
  · Copy all *.py files there.
  · Also copy the "gtk3.xml" file into /usr/share/streamtuner2/
  · Copy the channels/ subdir into /usr/share/streamtuner2/channels/
  · Install "bin" as /usr/bin/streamtuner2.
  · If you want to use another target, just edit the "bin" wrapper.
  · Optionally copy the help/ folder to /usr/share/docs/streamtuner2/
  · And the logo.png into the system pixmaps/,
    as well as the *.desktop file into /usr/share/applications/

That's pretty much what the binary packages extract to.


Startup errors
--------------

If streamtuner2 hangs at startup, you can manually enable the
debugging mode for more information.

Open a terminal window to start it. And use the `-D` flag to
enable extra output:

   streamtuner2 -D

Take note of any red error messages.

If it's just one channel plugin that hangs at startup, you
can alternatively disable it once:

   streamtuner2 -d xiph

Start the settings dialog (via F12) and press [save] there
if you wish to permanently disable it.

You can also manually edit the configuration file, located
in ~/.config/streamtuner2/settings.json


Hacking
-------

If you want to edit a channel plugin, just have a look into the
channels/*.py files. It's often rather easy to adapt things.

Moreover you can also edit the user interface. You need glade
installed, and open the "gtk3.xml" file. There it's easy to
rename or rearrange things.

Note that newer releases expect a compressed version of that
ui description. Use `make glade` simply, or `make gtk3` to
update the compressed version from the plain gtk.xml afterwards.


Sources
-------

You'll find the current source files under 
http://fossil.include-once.org/streamtuner2/

That's a fossil DVCS repository. Which is miles easier to use than
git. You can download the single binary from http://fossil-scm.org/
or from your distro, then check out the repo:

  fossil clone http://fossil.include-once.org/streamtuner2/ st2.fossil
  fossil open st2.fossil

Or browse the contents

  fossil ui

Alternatively there are git and svn exports.

  fossil export --svn

Or via

  http://fossil.include-once.org/streamtuner2/git-fast-export

You can send in patches, a fossil bundle, or set up your cloned
repo publically per `fossil cgi`. Else just create an account on
fossil.include-once.org, and send a mail, so I can elevate that
account to developer/commit/push permissions quickly. (Fossil
repos don't break. So dealing out sync access is a no-brainer.)


Alternatives
------------

See http://fossil.include-once.org/streamtuner2/wiki/alternatives
for a list of recommended alternatives. Future ST2 versions will
try to interface and share more with them.


License
-------

Public Domain. (Unrestricted copying, modification, etc.)

If you wish you could thus redistribute it under a BSD/MIT
or even GNU-style license.

(!) Plugins that fall under other licenses always carry a
custom `# license: …` comment.
