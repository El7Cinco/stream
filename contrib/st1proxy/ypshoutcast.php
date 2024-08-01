<html><body>
<h1> yp.shoutcast.com emulation </h1>
<h2> oh nooes, it haz no colors </h2>
<a href="/directory/?sgenre=Top+40">Top 40 (test)</a>
<pre>

# Add this to your /etc/hosts file:
<?php echo $_SERVER["SERVER_ADDR"]; ?>   yp.shoutcast.com  old.shoutcast.com

# And patch your streamtuner1 shoutcast.so plugin.
#   hexedit $(locate shoutcast.so)
# Change both occourences of "www.shoutcast.com" into "old.shoutcast.com".

</pre>
<?php
/**
 * api: php
 * title: yp.shoutcast.com emulation
 * description: fakes the old shoutcast directory, gets data from streamtuner2 cli
 * version: 0.4
 * support: untested
 * 
 *
 * You can set up this script as data gateway for streamtuner 0.99.99. It fetches
 * data from shoutcast using the streamtuner2 commandline interface and redisplays
 * it using the old YP html format.
 * If shoutcast 0.99.99 is then redirected to this script, on a local webserver,
 * it will magically be able to consume shoutcast again. Wacky workaround times.
 *
 * SETUP:
 *
 * 1. Your webserver must respond to the fake virtual hosts "yp.shoutcast.com"
 *    and "old.shoutcast.com".
 * 
 * 2. Install this script together with a streamtuner2 source package in a directory
 *    below docroot as /directory/index.php.
 *
 * 3. Add "127.0.0.1 yp.shoutcast.com ww2.shoutcast.com" in /etc/hosts to trick
 *    streamtuner1.
 *
 * Some versions of streamtuner1`s shoutcast.so plugin need to be patched to
 * look up "old.shoutcast.com" instead of the real "www.shoutcast.com".
 *
 */


# must be a world-writable directory (and then better contain a .htaccess to block it from outside access)
putenv("XDG_CONFIG_HOME=" . dirname(__FILE__)."/config");

# ST2 binary
$STREAMTUNER2 = "/usr/bin/streamtuner2";   # You could also use ./st2.py or e.g. ../src/st2.py



#-- generate a radio list
#$_REQUEST["sgenre"] = "Top 40";
if (isset($_REQUEST["sgenre"])) {


    # filter category
    $category = substr(preg_replace("/[^-\w_ ]+/", "", basename($_REQUEST["sgenre"])), 0, 20);
    
    # invoke streamtuner2
    $data = `$STREAMTUNER2 category shoutcast '$category'`;
    $data = json_decode($data, TRUE);
    
    # fake YP html
    foreach ($data as $i=>$row) {
    
        # be lazy
        $max = 2000;
        extract($row);
        
        #-- convert to old urls, else streamtuner1 won't see them
        preg_match("/(\d+)/", $url2=$url, $id);
        $id = $id[1];
        $url = "/sbin/shoutcast-playlist.pls?rn=$id&file=filename.pls";
        
        #-- remove invalid homepage URLs
        if (strpos($homepage, "shoutcast")) {
            $homepage = "http://www.google.com/search?q=$title";
        }

        
        # invalid html of yp.shoutcast.com is mimiced here
	print <<< __END__

    <tr>
      <td width="35" nowrap align="center" bgcolor="#001E5A"><font face="Arial, Helvetica" size="1" color="#FFFFFF"><b>$i</b></font></td>
      <td width="10" nowrap align="center" bgcolor="#001E5A">&nbsp;</td>
      <td nowrap align="center" bgcolor="#001E5A"><a href="$url"><img src="/images/tunein.gif" border="0" width="49" height="15"></a></font></td>
      <td width="10" nowrap align="center" bgcolor="#001E5A">&nbsp;</td>
      <td width="100%" align="left" bgcolor="#001E5A"><font face="Arial" size="2" color="#FFFFFF"><font size="1"><b>[$genre]</font></b> <font color=#ff0000 size=-2>CLUSTER </font><a id="listlinks" target="_scurl" href="$homepage">$title</a><br>
      <font size="1"><font color="#FF0000">Now Playing:</font> $playing</font></font></td>
      <td nowrap align="center" width="10" bgcolor="#001E5A">&nbsp;</td>
      <td nowrap align="center" bgcolor="#001E5A"><font face="Arial, Helvetica" size="2" color="#FFFFFF">$listeners/$max</font></td>
      <td nowrap align="center" width="10" bgcolor="#001E5A">&nbsp;</td>
      <td nowrap align="center" bgcolor="#001E5A"><font face="Arial, Helvetica" size="2" color="#FFFFFF">$bitrate</font></td>
      <td nowrap align="center" bgcolor="#001E5A" width="10">&nbsp;</td>
    </tr>
    <tr>
      <td colspan="10" nowrap align="center"></td>
    </tr>

__END__;

/*
        print <<< __END__

      <div class="old-shoutcast-entry">
        <a href="$url"><img src="tunein.gif"></a>
        <font color=blue><b>[$genre]</font></b>
        <a target="_scurl" href="$homepage">$title</a><br>
	<font color=green><font color=red>Now Playing:</font> $playing </font>
        <font face="grim">$listeners/$max</font>
        <font face="high">$bitrate</font>
      </div>

__END__;
*/
    }
}


#-- just dump genre list always
if (1) {  //isset($_REQUEST["genre"])) {

    # haha, it's just a fixed list
    $categories = json_decode('["Alternative", ["Adult Alternative", "Britpop", "Classic Alternative", "College", "Dancepunk", "Dream Pop", "Emo", "Goth", "Grunge", "Hardcore", "Indie Pop", "Indie Rock", "Industrial", "Modern Rock", "New Wave", "Noise Pop", "Power Pop", "Punk", "Ska", "Xtreme"], "Blues", ["Acoustic Blues", "Chicago Blues", "Contemporary Blues", "Country Blues", "Delta Blues", "Electric Blues"], "Classical", ["Baroque", "Chamber", "Choral", "Classical Period", "Early Classical", "Impressionist", "Modern", "Opera", "Piano", "Romantic", "Symphony"], "Country", ["Americana", "Bluegrass", "Classic Country", "Contemporary Bluegrass", "Contemporary Country", "Honky Tonk", "Hot Country Hits", "Western"], "Decades", ["30s", "40s", "50s", "60s", "70s", "80s", "90s"], "Easy Listening", ["Exotica", "Light Rock", "Lounge", "Orchestral Pop", "Polka", "Space Age Pop"], "Electronic", ["Acid House", "Ambient", "Big Beat", "Breakbeat", "Dance", "Demo", "Disco", "Downtempo", "Drum and Bass", "Electro", "Garage", "Hard House", "House", "IDM", "Jungle", "Progressive", "Techno", "Trance", "Tribal", "Trip Hop"], "Folk", ["Alternative Folk", "Contemporary Folk", "Folk Rock", "New Acoustic", "Traditional Folk", "World Folk"], "Inspirational", ["Christian", "Christian Metal", "Christian Rap", "Christian Rock", "Classic Christian", "Contemporary Gospel", "Gospel", "Southern Gospel", "Traditional Gospel"], "International", ["African", "Arabic", "Asian", "Bollywood", "Brazilian", "Caribbean", "Celtic", "Chinese", "European", "Filipino", "French", "Greek", "Hindi", "Indian", "Japanese", "Jewish", "Klezmer", "Korean", "Mediterranean", "Middle Eastern", "North American", "Russian", "Soca", "South American", "Tamil", "Worldbeat", "Zouk"], "Jazz", ["Acid Jazz", "Avant Garde", "Big Band", "Bop", "Classic Jazz", "Cool Jazz", "Fusion", "Hard Bop", "Latin Jazz", "Smooth Jazz", "Swing", "Vocal Jazz", "World Fusion"], "Latin", ["Bachata", "Banda", "Bossa Nova", "Cumbia", "Latin Dance", "Latin Pop", "Latin Rock", "Mariachi", "Merengue", "Ranchera", "Reggaeton", "Regional Mexican", "Salsa", "Tango", "Tejano", "Tropicalia"], "Metal", ["Black Metal", "Classic Metal", "Extreme Metal", "Grindcore", "Hair Metal", "Heavy Metal", "Metalcore", "Power Metal", "Progressive Metal", "Rap Metal"], "Misc", [], "New Age", ["Environmental", "Ethnic Fusion", "Healing", "Meditation", "Spiritual"], "Pop", ["Adult Contemporary", "Barbershop", "Bubblegum Pop", "Dance Pop", "Idols", "JPOP", "Oldies", "Soft Rock", "Teen Pop", "Top 40", "World Pop"], "Public Radio", ["College", "News", "Sports", "Talk"], "Rap", ["Alternative Rap", "Dirty South", "East Coast Rap", "Freestyle", "Gangsta Rap", "Hip Hop", "Mixtapes", "Old School", "Turntablism", "West Coast Rap"], "Reggae", ["Contemporary Reggae", "Dancehall", "Dub", "Ragga", "Reggae Roots", "Rock Steady"], "Rock", ["Adult Album Alternative", "British Invasion", "Classic Rock", "Garage Rock", "Glam", "Hard Rock", "Jam Bands", "Piano Rock", "Prog Rock", "Psychedelic", "Rockabilly", "Surf"], "Soundtracks", ["Anime", "Kids", "Original Score", "Showtunes", "Video Game Music"], "Talk", ["BlogTalk", "Comedy", "Community", "Educational", "Government", "News", "Old Time Radio", "Other Talk", "Political", "Scanner", "Spoken Word", "Sports", "Technology"], "Themes", ["Adult", "Best Of", "Chill", "Eclectic", "Experimental", "Female", "Heartache", "Instrumental", "LGBT", "Party Mix", "Patriotic", "Rainy Day Mix", "Reality", "Sexy", "Shuffle", "Travel Mix", "Tribute", "Trippy", "Work Mix"]]');

    # fake YP html
    print "<FORM ACTION=\"/directory/\"><SELECT NAME=\"sgenre\">\n";
    foreach ($categories as $cat) {
        if (is_array($cat)) {
            foreach ($cat as $sub) {
                print "\t\t<OPTION VALUE=\"$sub\">$sub\n";
            }
        }   # difference between sub and main category are just in the preceeding \tabs
        else {
            print "\t<OPTION VALUE=\"$cat\">$cat\n";
        }
    }
    print "</SELECT></FORM>\n";
}


?>
<s>Page 1 of 1</s>
</body></html>
