# encoding: utf-8
# api: python
# type: extract
# category: config
# title: Plugin configuration
# description: Read meta data, pyz/package contents, module locating
# version: 0.7.5
# state: stable
# classifiers: documentation
# license: PD
# priority: core
# docs: https://fossil.include-once.org/pluginspec/
# url: http://fossil.include-once.org/streamtuner2/wiki/plugin+meta+data
# config: -
#
# Provides plugin lookup and meta data extraction utility functions.
# It's used to abstract module+option management in applications.
# For consolidating internal use and external/tool accessibility.
#
# The key:value format is language-agnostic. It's basically YAML in
# a topmost script comment. For Python only # hash comments though.
# Uses common field names, a documentation block, and an obvious
# `config: { .. }` spec for options and defaults.
#
# It neither imposes a specific module/plugin API, nor config storage,
# and doesn't fixate module loading. It's really just meant to look
# up meta infos.
# This approach avoids in-code values/inspection, externalized meta
# descriptors, and any hodgepodge or premature module loading just to
# uncover module description fields.
#
# plugin_meta()
# ‾‾‾‾‾‾‾‾‾‾‾‾‾
#  Is the primary function to extract a meta dictionary from files.
#  It either reads from a given module= name, a literal fn=, or just
#  src= code, and as fallback inspects the last stack frame= else.
#
# module_list()
# ‾‾‾‾‾‾‾‾‾‾‾‾‾
#  Returns basenames of available/installed plugins. It uses the
#  plugin_base=[] list for module relation. Which needs to be set up
#  beforehand, or injected.
#
# add_plugin_defaults()
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  Populates a config_options{} and plugin_states{} list. Used for
#  initial setup, or when adding new plugins, etc. Both dicts might
#  also be ConfigParser stores, or implement magic __set__ handling
#  to act on state changes.
#
# get_data()
# ‾‾‾‾‾‾‾‾‾‾
#  Is mostly an alias for pkgutil.get_data(). It abstracts the main
#  base path, allows PYZ usage, and adds some convenience flags.‾
#  It's somewhat off-scope for plugin management, but used internally.
#
# argparse_map()
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  Converts a list of config: options with arg: attribute for use as
#  argparser parameters.
#
# dependency().depends()/.valid()
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  Probes a new plugins` depends: list against installed base modules.
#  Utilizes each version: fields and allows for virtual modules, or
#  alternatives and honors alias: names.
#
#
# Generally this scheme concerns itself more with plugin basenames.
# That is: module scripts in a package like `ext.plg1` and `ext.plg2`.
# It can be initialized by injecting the plugin-package basename into
# plugin_base = []. The associated paths will be used for module
# lookup via pkgutil.iter_modules().
#
# And a central module can be extended with new lookup locations best
# by attaching new locations itself via module.__path__ + ["./local"]
# for example.
#
# Plugin loading thus becomes as simple as __import__("ext.local").
# The attached plugin_state config dictionary in most cases can just
# list module basenames, if there's only one set to manage.


import sys
import os
import re
import pkgutil
import inspect
try:
    from distutils.spawn import find_executable
except:
    try: 
        from compat2and3 import find_executable
    except:
        def find_executable(str):
            pass
try:
    from gzip import decompress as gzip_decode  # Py3 only
except:
    try:
        from compat2and3 import gzip_decode   # st2 stub
    except:
        def gzip_decode(bytes):
            import zlib
            return zlib.decompress(bytes, 16 + zlib.MAX_WBITS)    # not fully compatible
import zipfile
import argparse

__all__ = [
    "get_data", "module_list", "plugin_meta",
    "dependency", "add_plugin_defaults"
]


# Injectables
# ‾‾‾‾‾‾‾‾‾‾‾
log_ERR = lambda *x: None

# File lookup relation for get_data(), should name a top-level package.
module_base = "config"         # equivalent PluginBase(package=…)

# Package/module names for module_list() and plugin_meta() lookups.
# All associated paths will be scanned for module/plugin basenames.
plugin_base = ["channels"]     # equivalent to `searchpath` in PluginBase


# Resource retrieval
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Fetches file content from install path or from within PYZ
# archive. This is just an alias and convenience wrapper for
# pkgutil.get_data().
# Utilizes the module_base / file_base as top-level reference.
#
def get_data(fn, decode=False, gz=False, file_base=None):
    try:
        bin = pkgutil.get_data(file_base or module_base, fn)
        if gz:
            bin = gzip_decode(bin)
        if decode:
            return bin.decode("utf-8", errors='ignore')
        else:
            return str(bin)
    except:
        # log_ERR("get_data() didn't find:", fn, "in", file_base)
        pass


# Plugin name lookup
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Search through ./plugins/ (and other configured plugin_base
# names → paths) and get module basenames.
#
def module_list(extra_paths=[]):

    # Convert plugin_base package names into paths for iter_modules
    paths = []
    for mp in plugin_base:
        if sys.modules.get(mp):
            paths += sys.modules[mp].__path__
        elif os.path.exists(mp):
            paths.append(mp)

    # Should list plugins within zips as well as local paths
    ls = pkgutil.iter_modules(paths + extra_paths)
    return [name for loader, name, ispkg in ls]


# Plugin => meta dict
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# This is a trivial wrapper to assemble a complete dictionary
# of available/installed plugins. It associates each plugin name
# with a its meta{} fields.
#
def all_plugin_meta():
    return {
        name: plugin_meta(module=name) for name in module_list()
    }


# Plugin meta data extraction
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Can fetch infos from different sources:
#
#   fn=      read literal files, or .pyz contents
#
#   src=     from already uncovered script code
#
#   module=  lookup per pkgutil, from plugin bases
#            or top-level modules
#
#   frame=   extract comment header of caller
#            (default)
#
def plugin_meta(fn=None, src=None, module=None, frame=1, extra_base=[]):

    # Try via pkgutil first,
    # find any plugins.* modules, or main packages
    if module:
        fn = module
        for base in plugin_base + extra_base:
            try:
                src = get_data(fn=fn+".py", decode=True, file_base=base)
                if src:
                    break
            except:
                continue  # plugin_meta_extract() will print a notice later

    # Real filename/path
    elif fn and os.path.exists(fn):
        src = open(fn).read(4096)

    # Else get source directly from caller
    elif not src and not fn:
        module = inspect.getmodule(sys._getframe(frame))
        fn = inspect.getsourcefile(module)
        src = inspect.getcomments(module)

    # Assume it's a filename within a zip
    elif fn:
        intfn = ""
        while fn and len(fn) and not os.path.exists(fn):
            fn, add = os.path.split(fn)
            intfn = add + "/" + intfn
        if len(fn) >= 3 and intfn and zipfile.is_zipfile(fn):
            src = zipfile.ZipFile(fn, "r").read(intfn.strip("/"))

    # Extract source comment into meta dict
    if not src:
        src = ""
    if not isinstance(src, str):
        src = src.decode("utf-8", errors='replace')
    return plugin_meta_extract(src, fn)


# Comment and field extraction logic
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Finds the first comment block. Splits key:value header
# fields from comment. Turns everything into an dict, with
# some stub fields if absent.
#
def plugin_meta_extract(src="", fn=None, literal=False):

    # Defaults
    meta = {
        "id": os.path.splitext(os.path.basename(fn or ""))[0],
        "fn": fn,
        "api": "python",
        "type": "module",
        "category": None,
        "priority": None,
        "version": "0",
        "title": fn,
        "description": "no description",
        "config": [],
        "doc": ""
    }

    # Extract coherent comment block
    src = src.replace("\r", "")
    if not literal:
        src = rx.comment.search(src)
        if not src:
            log_ERR("Couldn't read source meta information:", fn)
            return meta
        src = src.group(0)
        src = rx.hash.sub("", src).strip()

    # Split comment block
    if src.find("\n\n") > 0:
        src, meta["doc"] = src.split("\n\n", 1)

    # Turn key:value lines into dictionary
    for field in rx.keyval.findall(src):
        meta[field[0].replace("-", "_")] = field[1].strip()
    meta["config"] = plugin_meta_config(meta.get("config") or "")

    return meta


# Unpack config: structures
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Further breaks up the meta['config'] descriptor.
# Creates an array from JSON/YAML option lists.
#
# config:
#   { name: 'var1', type: text, value: "default, ..." }
#   { name=option2, type=boolean, $value=1, etc. }
#
# Stubs out name, value, type, description if absent.
#
def plugin_meta_config(str):
    config = []
    for entry in rx.config.findall(str):
        entry = entry[0] or entry[1]
        opt = {
            "type": None,
            "name": None,
            "description": "",
            "value": None
        }
        for field in rx.options.findall(entry):
            opt[field[0]] = (field[1] or field[2] or field[3] or "").strip()
        # normalize type
        opt["type"] = config_opt_type_map.get(opt["type"], opt["type"] or "str")
        # preparse select:
        if opt.get("select"):
            opt["select"] = config_opt_parse_select(opt.get("select", ""))
        config.append(opt)
    return config

# split up `select: 1=on|2=more|3=title` or `select: foo|bar|lists`
def config_opt_parse_select(s):
    if re.search("([=:])", s):
        return dict(rx.select_dict.findall(s))
    else:
        return dict([(v, v) for v in rx.select_list.findall(s)])

# normalize type:names to `str`, `text`, `bool`, `int`, `select`, `dict`
config_opt_type_map = dict(
    longstr="text", string="str", boolean="bool", checkbox="bool", integer="int", number="int",
    choice="select", options="select", table="dict", array="dict"
)


# Comment extraction regexps
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Pretty crude comment splitting approach. But works
# well enough already. Technically a YAML parser would
# do better; but is likely overkill.
#
class rx:
    comment = re.compile(r"""(^ {0,4}#.*\n)+""", re.M)
    hash = re.compile(r"""(^ {0,4}# {0,3}\r*)""", re.M)
    keyval = re.compile(r"""
        ^([\w-]+):(.*$(?:\n(?![\w-]+:).+$)*)      # plain key:value lines
    """, re.M | re.X)
    config = re.compile(r"""
        \{ (.+?) \} | \< (.+?) \>              # JSOL/YAML scheme {...} dicts
    """, re.X)
    options = re.compile(r"""
        ["':$]?   (\w*)  ["']?                 # key or ":key" or '$key'
        \s* [:=] \s*                           # "=" or ":"
     (?:  "  ([^"]*)  "
       |  '  ([^']*)  '                        #  "quoted" or 'singl' values
       |     ([^,]*)                           #  or unquoted literals
     )
    """, re.X)
    select_dict = re.compile(r"(\w+)\s*[=:>]+\s*([^=,|:]+)")
    select_list = re.compile(r"\s*([^,|;]+)\s*")



# ArgumentParser options conversion
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# As variation of in-application config: options, this method converts
# cmdline argument specifiers.
#
#  config:
#    { arg: -i, name: input[], type: str, description: input files }
#
# Which allows to collect argumentparser options from different plugins.
# The only difference to normal config entries is the `arg:` attribute.
#
#  · It adds array arguments with a [] name suffix, or a `*` type suffix.
#    Else even a `?` or `+` and numeric counts after the type flag.
#
#  · Understands the types `str`, `int` and `bool`.
#
#  · Entries may carry a `hidden: 1` or `required: 1` attribute.
#
#  · And `help:` is an alias to `description:`
#    And `default:` an alias for `value:`
#
#  · While `type: select` utilizes the `select: a|b|c` format as usual.
#
# ArgParsers const=, metavar= flag, or type=file are not aliased here.
#
# Basically returns a dictionary that can be fed per **kwargs directly
# to an ArgumentParsers add_argument(). Iterate over each plugins
# meta['config'][] options to convert them.
#
def argparse_map(opt):
    if not ("arg" in opt and opt["name"] and opt["type"]):
        return {}

    # Extract --flag names
    args = opt["arg"].split() + re.findall(r"-+\w+", opt["name"])

    # Prepare mapping options
    typing = re.findall(r"bool|str|\[\]|const|false|true", opt["type"])
    naming = re.findall(r"\[\]", opt["name"])
    name = re.findall(r"(?<!-)\b\w+", opt["name"])
    nargs = re.findall(r"\b\d+\b|[\?\*\+]", opt["type"]) or [None]
    is_arr = "[]" in (naming + typing) and nargs == [None]
    is_bool = "bool" in typing
    false_b = "false" in typing or opt["value"] in ("0", "false")
    # print("\nname=", name, "is_arr=", is_arr, "is_bool=", is_bool,
    # "bool_d=", false_b, "naming=", naming, "typing=", typing)

    # Populate combination as far as ArgumentParser permits
    kwargs = dict(
        args     = args,
        dest     = name[0] if not name[0] in args else None,
        action   = is_arr and "append"
                   or  is_bool and false_b and "store_false"
                   or  is_bool and "store_true"  or  "store",
        nargs    = nargs[0],
        default  = opt.get("default") or opt["value"],
        type     = None if is_bool  else  ("int" in typing and int
                   or  "bool" in typing and bool  or  str),
        choices  = opt["select"].split("|") if "select" in opt else None,
        required = "required" in opt or None,
        help     = opt["description"] if not "hidden" in opt
                   else argparse.SUPPRESS
    )
    return {k: w for k, w in kwargs.items() if w is not None}


# Minimal depends: probing
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Now this definitely requires customization. Each plugin can carry
# a list of (soft-) dependency names.
#
#   depends: config, appcore >= 2.0, bin:wkhtmltoimage, python < 3.5
#
# Here only in-application modules are honored, system references
# ignored. Unknown plugin names are also skipped. A real install
# helper might want to auto-tick them on, etc. This example is just
# meant for probing downloadable plugins.
#
# The .valid() helper only asserts the api: string, or skips existing
# modules, and if they're more recent.
# While .depends() compares minimum versions against existing modules.
#
# In practice there's little need for full-blown dependency resolving
# for application-level modules.
#
class dependency(object):

    # prepare list of known plugins and versions
    def __init__(self, add={}, core=["st2", "uikit", "config", "action"]):
        self.have = {
            "python": { "version": sys.version }
        }
        # inject virtual modules
        for name, meta in add.items():
            if isinstance(meta, bool): meta = 1 if meta else -1
            if isinstance(meta, tuple): meta = ".".join(str(n) for n in meta)
            if isinstance(meta, (int, float, str)): meta = {"version": str(meta)}
            self.have[name] = meta
        # read plugins/*
        self.have.update(all_plugin_meta())
        # add core modules
        for name in core:
            self.have[name] = plugin_meta(module=name, extra_base=["config"])
        # aliases
        for name, meta in self.have.copy().items():
            if meta.get("alias"):
                for alias in re.split(r"\s*[,;]\s*", meta["alias"]):
                    self.have[alias] = self.have[name]

    # basic plugin pre-screening (skip __init__, filter by api:,
    # exclude installed & same-version plugins)
    def valid(self, newpl, _log=lambda *x:0):
        id = newpl.get("$name", "__invalid")
        have_ver = self.have.get(id, {}).get("version", "0")
        if id.find("__") == 0:
            _log("wrong id")
            pass
        elif newpl.get("api") not in ("python", "streamtuner2"):
            _log("wrong api")
            pass
        elif set((newpl.get("status"), newpl.get("priority"))).intersection(set(("obsolete", "broken"))):
            _log("wrong status")
            pass
        elif have_ver >= newpl.get("version", "0.0"):
            _log("newer version already installed")
            pass
        else:
            return True

    # Verify depends: and breaks: against existing plugins/modules
    def depends(self, plugin, _log=lambda *x:0):
        r = True
        if plugin.get("depends"):
            r &= self.and_or(self.split(plugin["depends"]), self.have)
        if plugin.get("breaks"):
            r &= self.neither(self.split(plugin["breaks"]), self.have)
        _log(r)
        return r

    # Split trivial "pkg | alt, mod >= 1, uikit < 4.0" string into nested list [[dep],[alt,alt],[dep]]
    def split(self, dep_str):
        dep_cmp = []
        for alt_str in re.split(r"\s*[,;]+\s*", dep_str):
            alt_cmp = []
            # split alternatives |
            for part in re.split(r"\s*\|+\s*", alt_str):
                # skip deb:pkg-name, rpm:name, bin:name etc.
                if not len(part):
                    continue
                if part.find(":") >= 0:
                    self.have[part] = { "version": self.module_test(*part.split(":")) }
                # find comparison and version num
                part += " >= 0"
                m = re.search(r"([\w.:-]+)\s*\(?\s*([>=<!~]+)\s*([\d.]+([-~.]\w+)*)", part)
                if m and m.group(2):
                    alt_cmp.append([m.group(i) for i in (1, 2, 3)])
            if alt_cmp:
                dep_cmp.append(alt_cmp)
        return dep_cmp

    # Single comparison
    def cmp(self, d, have, absent=True):
        name, op, ver = d
        # absent=True is the relaxed check, will ignore unknown plugins // set absent=False or None for strict check (as in breaks: rule e.g.)
        if not have.get(name, {}).get("version"):
            return absent
        # curr = installed version
        curr = have[name]["version"]
        tbl = {
            ">=": curr >= ver,
            "<=": curr <= ver,
            "==": curr == ver,
            ">":  curr > ver,
            "<":  curr < ver,
            "!=": curr != ver,
        }
        r = tbl.get(op, True)
        #print "log.VERSION_COMPARE: ", name, " → (", curr, op, ver, ") == ", r
        return r

    # Compare nested structure of [[dep],[alt,alt]]
    def and_or(self, deps, have, r = True):
        #print deps
        return not False in [True in [self.cmp(d, have) for d in alternatives] for alternatives in deps]

    # Breaks/Conflicts: check [[or],[or]]
    def neither(self, deps, have):
        return not True in [self.cmp(d, have, absent=None) for cnd in deps for d in cnd]

    # Resolves/injects complex "bin:name" or "python:name" dependency URNs
    def module_test(self, type, name):
        return "1"  # disabled for now
        if "_" + type in dir(self):
            return "1" if bool(getattr(self, "_" + type)(name)) else "-1"
    # `bin:name` lookup
    def _bin(self, name):
        return find_executable(name)
    # `python:module` test
    def _python(self, name):
        return __import__("imp").find_module(name) is not None


# Add plugin defaults to conf.* store
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Utility function which applies plugin meta data to a config
# store. Which in the case of streamtuner2 is really just a
# dictionary `conf{}` and a plugin list in `conf.plugins{}`.
#
# Adds each default option value: to conf_options{}. And sets
# first plugin state (enabled/disabled) in conf_plugins{} list,
# depending on priority: classifier.
#
def add_plugin_defaults(conf_options, conf_plugins, meta={}, module=""):

    # Option defaults, if not yet defined
    for opt in meta.get("config", []):
        if "name" in opt and "value" in opt:
            _value = opt.get("value", "")
            _name = opt.get("name")
            _type = opt.get("type")
            if _name not in conf_options:
                # typemap
                if _type == "bool":
                    val = _value.lower() in ("1", "true", "yes", "on")
                elif _type == "int":
                    val = int(_value)
                elif _type in ("table", "list"):
                    val = [ re.split(r"\s*[,;]\s*", s.strip()) for s in re.split(r"\s*[|]\s*", _value) ]
                elif _type == "dict":
                    val = dict([ re.split(r"\s*(?:=>+|==*|-+>|:=+)\s*", s.strip(), 1) for s in re.split(r"\s*[|;,]\s*", _value) ])
                else:
                    val = str(_value)
                conf_options[_name] = val

    # Initial plugin activation status
    if module and module not in conf_plugins:
        conf_plugins[module] = meta.get("priority") in (
            "core", "builtin", "always", "default", "standard"
        )


