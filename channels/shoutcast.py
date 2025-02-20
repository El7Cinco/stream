# api: streamtuner2
# title: Shoutcast.com
# description: Primary list of shoutcast servers (now managed by radionomy).
# type: channel
# category: radio
# author: Mario
# original: Jean-Yves Lefort
# version: 1.6
# url: http://directory.shoutcast.com/
# config:
#    { name: shoutcast_format, type: select, select: pls|m3u|xspf, value: pls, description: "Shoutcast playlist format to retrieve" }
# priority: default
# png:
#   iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAelJREFUOI2NU0toE2EYnM12t2wLkhSXSIgEJMHFQ2naQ+kpoPYQoaXH3gRFsegloUhRQTyU2oOgggQUzzlEQomIBzU+EHooBIol0cOGLqFFFiJ5SB5skvFU6ebRduA7/DAz
#   /PM9BJLoh3Q6zVQqBZfLhXq9jlAohHA4LHTzhvqJ2+02c7kcgsEgfD4fRFFEPp+HZVmUJEk41kAURcHv99Pj8cAwDGiaBkVR0C0GAJDsW7VajYVCgYlEguVymZZlsVKpcG1tlYd5fX8AAIqiCF6vF6VSibIsI5lMYvvDE1xymwDu/ec5BhkcIJPJIHJzFqf372P1cgMf
#   f46cLIKu61yJXufr5VO0voyzEZ/k8sI4s9ns0RFarRZjL56inIshekWGenYS6IzhR9PCntRBIBCw8XsiFItFNLMxPJgfwVjDi4Y8g2b9DILaMKZGd2Ca5tEGiqJg2xjF200H6J+AvKtjeG8T3998xW5nAk6n08bviSBJEqhewLlpN4bMHfwxfuH5J8J98SGerS/B4XDY
#   d+FwQ6rVKm8vXeP++6vku2lu3FEZubFIXdc5qNm2x93ILZobszRfaYwuaIzH4wOFfafwt7CFb59/Y0uYx8rLR1BVtXd1u2AzCMwsQg6cx+O5uWOFBxAGnfNJ8Q/z/DNTtgbnsgAAAABJRU5ErkJggg==
# depends: re, ahttp
# extraction-method: json, regex
#
# Shoutcast is a server software for audio streaming. It automatically spools
# station information on shoutcast.com, which today lists over 60000 radios.
#
# It has been aquired by Radionomy in 2014. Since then significant changes
# took place. The former yellow pages API got deprecated. Streamtuner2 now
# utilizes the AJAX interface for speedy playlist discovery
#


import ahttp
from json import loads as json_decode
import re
from config import *
from channels import *
import channels



# SHOUTcast data module
#
# Former API doc: http://wiki.winamp.com/wiki/SHOUTcast_Radio_Directory_API 
# But neither their Wiki nor Bulletin Board provide concrete information on
# the eligibility of open source desktop apps for an authhash.
#
# Therefore we'll be retrieving stuff from the homepage still. The new
# interface conveniently uses JSON already, so let's use that:
#
#   POST http://www.shoutcast.com/Home/BrowseByGenre {genrename: Pop}
#
# We do need a catmap now too, but that's easy to aquire and will be kept
# within the cache dirs.
#
class shoutcast(channels.ChannelPlugin):

    # attrs
    base_url = "http://directory.shoutcast.com/"
    listformat = "pls"
    has_search = False
    
    # categories
    categories = []
    catmap = {"Choral": 35, "Winter": 275, "JROCK": 306, "Motown": 237, "Political": 290, "Tango": 192, "Ska": 22, "Comedy": 283, "Decades": 212, "European": 143, "Reggaeton": 189, "Islamic": 307, "Freestyle": 114, "French": 145, "Western": 53, "Dancepunk": 6, "News": 287, "Xtreme": 23, "Bollywood": 138, "Celtic": 141, "Kids": 278, "Filipino": 144, "Hanukkah": 270, "Greek": 146, "Punk": 21, "Spiritual": 211, "Industrial": 14, "Baroque": 33, "Talk": 282, "JPOP": 227, "Scanner": 291, "Mediterranean": 154, "Swing": 174, "Themes": 89, "IDM": 75, "40s": 214, "Funk": 236, "Rap": 110, "House": 74, "Educational": 285, "Caribbean": 140, "Misc": 295, "30s": 213, "Anniversary": 266, "Sports": 293, "International": 134, "Tribute": 107, "Piano": 41, "Romantic": 42, "90s": 219, "Latin": 177, "Grunge": 10, "Dubstep": 312, "Government": 286, "Country": 44, "Salsa": 191, "Hardcore": 11, "Afrikaans": 309, "Downtempo": 69, "Merengue": 187, "Psychedelic": 260, "Female": 95, "Bop": 167, "Tribal": 80, "Metal": 195, "70s": 217, "Tejano": 193, "Exotica": 55, "Anime": 277, "BlogTalk": 296, "African": 135, "Patriotic": 101, "Blues": 24, "Turntablism": 119, "Chinese": 142, "Garage": 72, "Dance": 66, "Valentine": 273, "Barbershop": 222, "Alternative": 1, "Technology": 294, "Folk": 82, "Klezmer": 152, "Samba": 315, "Turkish": 305, "Trance": 79, "Dub": 245, "Rock": 250, "Polka": 59, "Modern": 39, "Lounge": 57, "Indian": 149, "Hindi": 148, "Brazilian": 139, "Eclectic": 93, "Korean": 153, "Creole": 316, "Dancehall": 244, "Surf": 264, "Reggae": 242, "Goth": 9, "Oldies": 226, "Zouk": 162, "Environmental": 207, "Techno": 78, "Adult": 90, "Rockabilly": 262, "Wedding": 274, "Russian": 157, "Sexy": 104, "Chill": 92, "Opera": 40, "Emo": 8, "Experimental": 94, "Showtunes": 280, "Breakbeat": 65, "Jungle": 76, "Soundtracks": 276, "LoFi": 15, "Metalcore": 202, "Bachata": 178, "Kwanzaa": 272, "Banda": 179, "Americana": 46, "Classical": 32, "German": 302, "Tamil": 160, "Bluegrass": 47, "Halloween": 269, "College": 300, "Ambient": 63, "Birthday": 267, "Meditation": 210, "Electronic": 61, "50s": 215, "Chamber": 34, "Heartache": 96, "Britpop": 3, "Soca": 158, "Grindcore": 199, "Reality": 103, "00s": 303, "Symphony": 43, "Pop": 220, "Ranchera": 188, "Electro": 71, "Christmas": 268, "Christian": 123, "Progressive": 77, "Jazz": 163, "Trippy": 108, "Instrumental": 97, "Tropicalia": 194, "Fusion": 170, "Healing": 209, "Glam": 255, "80s": 218, "KPOP": 308, "Worldbeat": 161, "Mixtapes": 117, "60s": 216, "Mariachi": 186, "Soul": 240, "Cumbia": 181, "Inspirational": 122, "Impressionist": 38, "Gospel": 129, "Disco": 68, "Arabic": 136, "Idols": 225, "Ragga": 247, "Demo": 67, "LGBT": 98, "Honeymoon": 271, "Japanese": 150, "Community": 284, "Weather": 317, "Asian": 137, "Hebrew": 151, "Flamenco": 314, "Shuffle": 105}
    
    # redefine
    streams = {}
    
    def init2(self, parent):
        if "shoutcast_format" in conf:
            self.listformat = conf.shoutcast_format
    
        
    # Extracts the category list from www.shoutcast.com,
    # stores a catmap (title => id)
    def update_categories(self):
        html = ahttp.get(self.base_url)
        #log.DATA( html )
        self.categories = []
        
        # Genre list in sidebar
        """
           <li id="genre-3" class="sub-genre " genreid="3" parentgenreid="1">
                <a href="/Genre?name=Britpop" onclick="return loadStationsByGenre('Britpop', 3, 1);">Britpop</a>
           </li>
        """
        rx = re.compile(r"loadStationsByGenre\(  '([^']+)' [,\s]* (\d+) [,\s]* (\d+)  \)", re.X)
        subs = rx.findall(html)

        # group
        current = []
        for (title, id, main) in subs:
            self.catmap[title] = int(id)
            if not int(main):
                self.categories.append(title)
                current = []
                self.categories.append(current)
            else:
                current.append(title)

        # .categories/.catmap get saved by reload_categories()
        pass
        

    # downloads stream list from shoutcast for given category
    def update_streams(self, cat):

        # page
        url = self.base_url + "Home/BrowseByGenre"
        params = { "genrename": cat }
        referer = self.base_url
        try:
            json = ahttp.get(url, params=params, referer=referer, post=1, ajax=1)
            json = json_decode(json)
        except:
            log.ERR("HTTP request or JSON decoding failed. Outdated python/requests perhaps.")
            return []
        self.parent.status(0.75)

        # remap JSON
        """
            AACEnabled:0
            Bitrate:128
            CurrentTrack:"Bolland & Bolland - Answer For A Lifetime"
            Format:"audio/mpeg"
            Genre:"Folk Rock"
            ID:99180411
            IceUrl:"AOLMRadio"
            IsAACEnabled:false
            IsPlaying:false
            IsRadionomy:true
            Listeners:159
            Name:"AOLMRadio"
            StreamUrl:null
        """
        entries = []
        for e in json:
            entries.append({
                "id": int(e.get("ID", 0)),
                "genre": str(e.get("Genre", "")),
                "title": str(e.get("Name", "")),
                "playing": str(e.get("CurrentTrack", "")),
                "bitrate": int(e.get("Bitrate", 0)),
                "listeners": int(e.get("Listeners", 0)),
                "url": "http://yp.shoutcast.com/sbin/tunein-station.%s?id=%s" % (self.listformat, e.get("ID", "0")),
                "listformat": self.listformat,
                "homepage": "",
                "format": str(e.get("Format", ""))
            })

        #log.DATA(entries)
        return entries

