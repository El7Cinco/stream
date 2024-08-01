# encoding: UTF-8
# api: streamtuner2
# title: radio.net
# description: Europe's biggest radio platform
# url: http://radio.net/
# version: 1.2
# type: channel
# category: radio
# png:
#   iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAt0lEQVR42mNgYGD4r+Ar/F/BDwkD+SBxojBMs1mLPBArgGlFqEEENYMNQNLsukIDYkirAvGu
#   ABsA1OC6XOP/5f8nwIaYAg0k2gBFsAsgTgcZkvnfDugFEeK9AFKsCPMG0CU6eZJgQ4R1eP8H7LLEivWyFJANQcQCLPBAmkGG4MJohmA6C6QA5gI5OxEUDNII
#   MwSvASBFIA3ociCxkWQAKMDICkSQIpgh2LDnSmP80YhsCFEJiRIMADpmeUOpqgjRAAAAAElFTkSuQmCC
# priority: optional
# extraction-method: regex
#
# Radio.net lists around 20.000 worldwide radio stations.
# A maximum of three pages from each genre are fetched here,
# some of the empty categories already omitted.
#
# The website heavily depends on JavaScript, a Flash player,
# some social tracking cookies. Now requires additional page
# request to get real streaming url, but at least no more
# expiring access key.


import time
import json
import re
import traceback
from config import *
from channels import *
import ahttp
import action


# obsolete: hook special JSON format in to avoid grepping images by generic handler
action.playlist_fmt_prio.insert(5, "rnjs")
action.playlist_content_map.insert(7, ("rnjs", r'"logo175x175rounded"'))
action.extract_playlist.extr_urls["rnjs"] = dict(
    url   = r" (?x) \"streamUrl\" \s*:\s* \"(\w+:\\?/\\?/[^\"]+)\" ",
    title = r" (?x) \"(?:description|seoTitle)\" \s*:\s* \"([^\"]+)\" ",
    unesc = "json",
)


# Radio.net
#
# · Uses HTML block-wise regex extraction.
#   → <div class="sc-1crnfmg-11 sc-1crnfmg-12 cYzyuZ"><a href="/s/kissfmuk">
#   → basically just title/url, images in a separate json blob
#
# · Currently using an urn: to resolve stream urls at play time.
#
# previously:
# · There's an API key in each page listing, contained in a script block
#   as `apiKey: '…'?`
# · Which is needed for generating the station info JSON urls:
#   → https://api.radio.net/info/v2/search/station?apikey=…&pageindex=1&station=STNAME
# · To extract these JSON info targets, a custom extraction recipie is injected
#   into the action module.
#   → "streamUrl": and "description": are scanned for.
#
# todo:
# · https://prod.radio-api.net/stations/local?count=10
#
class radionet (ChannelPlugin):

    # control flags
    has_search = False
    audioformat = "audio/mpeg"
    listformat = "href"
    titles = dict(listeners=False, playing="Description")
    img_resize = 33

    # sources
    apiPrefix = "https://api.radio.net/info/v2"
    genre_url = "http://www.radio.net/genre/{}"
    apiKey = None
    
    
    # Retrieve cat list and map
    def update_categories(self):
        html = ahttp.get("http://www.radio.net/genre")
        self.set_key(html)
        ls = re.findall("""<a class="[^"]+" href="/genre/(\w+)">([^<]+)</a>""", html)
        self.categories = ["Top 40 and Charts"] + [i[1] for i in ls]


    # Fetch entries
    def update_streams(self, cat, search=None):

        # category page, get key
        urlcat = cat.replace(" ", "-").lower()
        self.status(0.1)
        html = ahttp.get(self.genre_url.format(urlcat))
        for p in range(2, 4):
            self.status(p / 5.5)
            if html.find('?p={}"'.format(p)) >= 0:
                html += ahttp.get(self.genre_url.format(urlcat) + "?p={}".format(p))
        self.set_key(html)
        r = []
        
        # fetch JSON
        ls_json = re.findall("<script\sid=\"__NEXT_DATA__\"[^>]*>(\{.+?\})[;<]", html)
        if ls_json:
            try:
                return self.from_json(ls_json)
            except:
                log.error("JSON extraction failed", traceback.format_exc())
        
        # prefetch images from embedded json (genres and location would also be sourceable from "playables":[…])
        imgs = dict(re.findall('\],"id":"(\w+)","logo100x100":"(htt[^"]+)",', html))
        #log.DATA(imgs)

        # top 100 of the most horrible html serializations
        """
            <div class="sc-1crnfmg-9 sc-1crnfmg-10 kqrZgK"><a title="Listen
            to the station 1LIVE online now" data-testid="list-item"
            target="_self" href="/s/1live"><div class="sc-1crnfmg-7
            hlHPMo"><div class="sc-1crnfmg-0 fBSron"><div
            class="lazyload-wrapper "><div
            class="lazyload-placeholder"></div></div></div><div
            class="sc-1crnfmg-1 eOYJrC"><div class="sc-1crnfmg-2
            eBaEwX">1LIVE</div><div class="sc-1crnfmg-4 cKweix">Cologne,
            Pop</div><div class="sc-1crnfmg-5
,            kTPZiR"></div></div></div></a></div>
        """
        rx = re.compile("""
              <a\s+[^>]*\\bhref="(?:https?:)?(?://(?:[\w-]+)\.radio\.net)?/s/([^"]+)/?"> .{0,500}?
              <div[^>]+> (\w[^<]+) </div> .*?
              <div[^>]+> (\w[^/,]+) \s* [,/] \s+ (\w.+?)</div> 
            """, re.X|re.S
        )
        # extract text fields
        for d in re.findall(rx, html):
            #log.DATA_ROW(d)
            href, title, location, desc = d
            
            # refurbish extracted strings
            r.append(dict(
                name = href,
                genre = unhtml(desc),
                title = unhtml(title),
                playing = unhtml(location),
                url = "urn:radionet:"+href,
                homepage = "http://www.radio.net/s/{}".format(href),
                img = imgs.get(href, "https://www.radio.net/favicon.ico"),
            ));
        return r

    # process json
    def from_json(self, ls_json):
        ls = []
        for js in ls_json:
            js = json.loads(js)
            #print(json.dumps(js, indent=4))
            ls += js["props"]["pageProps"]["data"]["stations"]["playables"]
            #ls += js["data"]["stations"]["playables"]
        r = []
        for row in ls:
            href = row["id"]
            r.append(dict(
                name = href,
                title = row["name"],
                genre = ",".join(row.get("genres", [])),
                url = "urn:radionet:"+href,
                playing = row.get("city", row.get("country", "-")),
                homepage = "http://www.radio.net/s/{}".format(href),
                img = row["logo100x100"],
            ))
            print(row)
        return r

    # api search is gone, now requires to fetch streamUrl from per-radio homepage
    def resolve_urn(self, row):
        if row.get("url", "-").find("urn:radionet:") != 0:
            return
        html = ahttp.get(row["homepage"])
        stream = re.findall('"stream[s:[{"\s]+url"[\s:]+"([^"]+)"', html, re.S|re.I)
        if stream:
            row["url"] = stream[0]
            return row


    # extract JavaScript key from any HTML blob (needed for station query)
    def set_key(self, html):
        ls = re.findall("""apiKey: '(\w+)'""", html)
        if ls:
            self.apiKey = ls[0]



