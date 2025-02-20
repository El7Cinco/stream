# encoding: UTF-8
# api: streamtuner2
# title: Delicast
# description: directory of streaming media
# url: http://delicast.com/
# version: 0.8
# type: channel
# category: radio
# priority: obsolete
# config: -
# png:
#    iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAAAAAA6mKC9AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAA
#    AmJLR0QA/4ePzL8AAAAHdElNRQffBB4UJAsX77G0AAAANUlEQVQY02OwQwMMdv/BAEUASCFEoAIIEZIEIGYjBCAUwpb/6O5ACEABGQJ2cFsQIlB3oAEA6iVo+vl+BbQA
#    AAAldEVYdGRhdGU6Y3JlYXRlADIwMTUtMDQtMzBUMjI6MzY6MDMrMDI6MDAFLUvfAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE1LTA0LTMwVDIyOjM2OjAzKzAyOjAwdHDz
#    YwAAAABJRU5ErkJggg==
# priority: rare
# extraction-method: regex, action-handler
#
# Just a standard genre/country radio directory. Not very
# suitable for extraction actually, because it requires a
# second page request for uncovering the streaming URLs.
#
# Audio URL lookup is done in urn_resolve action handler now,
# so only happens on playback. Which of course won't allow for
# exporting/bookmarking etc.
# Now fetches up to 5 pages (20 entries each).


import re
from config import *
from channels import *
import ahttp
import action


# Delayed streaming URL discovery
class delicast (ChannelPlugin):

    # control flags
    has_search = False
    listformat = "srv"
    audioformat = "audio/mpeg"
    titles = dict(listeners=False, bitrate=False, playing="Location")

    categories = ["60s", "70s", "80s", "90s", "Alternative", "Blues",
    "Chillout", "Christian", "Classical", "Community", "Country", "Culture",
    "Dance", "Disco", "Easy listening", "Electronic", "Folk", "Funk",
    "Gospel", "Hiphop", "House Indie", "Information", "Jazz", "Latin",
    "Lounge", "Love", "Metal", "Oldies", "Pop", "R n b", "Reggae", "Rock",
    "Romantic", "Soul", "Sports", "Student", "Talk", "Techno", "Trance",
    "Urban", "World music"]
    

    # static
    def update_categories(self):
        pass


    # Fetch entries
    def update_streams(self, cat, search=None):

        ucat = re.sub("\W+", "-", cat.lower())
        html = ""
        for i in range(1, 5):
            add = ahttp.get("http://delicast.com/radio/q:" + ucat + ("" if i == 1 else "/%s" % i))
            html += add
            if not re.search("href='http://delicast.com/radio/q:%s/%s'" % (ucat, i+1), add):
                break
        r = []
        log.HTML(html)
        for ls in re.findall("""
                <b>\d+</b>\.
                .*?
                <a[^>]+href="(http[^"]+/radio/\w+)"
                .*?
                /pics/((?!play_tri)\w+)
                .*?
                120%'>([^<>]+)</span>
            """, html, re.X|re.S):
            if len(ls):
                homepage, country, title = ls
                r.append(dict(
                    homepage = homepage,
                    playing = country,
                    title = unhtml(title),
                    url = "urn:delicast",
                    genre = cat,
             #      genre = unhtml(tags),
                ))
        return r
      

    # Update `url` on station data access (incurs a delay for playing or recording)
    def resolve_urn(self, row):
        if row.get("url").startswith("urn:delicast"):
            html = ahttp.get(row["homepage"])
            ls = re.findall("^var url = \"(.+)\";", html, re.M)
            if ls:
                row["url"] = unhtml(ls[0])
            else:
                log.ERR("No stream found on %s" % row["homepage"])
        return row

