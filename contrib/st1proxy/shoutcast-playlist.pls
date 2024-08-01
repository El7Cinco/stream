<?php
/**
 * Second part wrapper for yp.shoutcast.com emulation
 *
 * Rewrites old form:
 *    /sbin/shoutcast-playlist.pls?rn=2329&file=filename.pls
 * to:
 *    http://yp.shoutcast.com/sbin/tunein-station.pls?id=4256
 *
 *
 * Needs to be installed in /sbin/, and be callable without .php
 * extension. Try one of these .htaccess directives:
 *
 *    SetHandler application/x-httpd-php
 * (
 * or
 *    Options +MultiViews
 * or
 *    AddHandler php-script .pls
 * or
 *    RewriteRule .pls .pls.php
 * or
 *    AddType application/x-httpd-php .pls
 * )
 *
 *
 * The web server should respond to the virtual hosts
 * "yp.shoutcast.com" and "old.shoutcast.com".
 *
 *
 */


#-- redirect
$id = @$_GET["rn"] . @$_GET["id"];
header("Location: http://www.shoutcast.com/sbin/tunein-station.pls?id=$id");
       # Note must redirect to //www.shoutcast, not to //yp.shoutcast
       # because else wrapper on localhost would get called in a loop.
       
       
#-- alternative
if (FALSE)
{
    header("Content-Type: audio/x-scpls");
    print file_get_contents("http://shoutcast.com/sbin/tunein-station.pls?id=$id");
}


?>