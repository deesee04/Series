# coding=utf8
###
# Copyright (c) 2010, Terje Hoås
# Copyright (c) 2014, spline
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

# my libs
try: # xml handling.
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Series')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class Series(callbacks.Plugin):
    """This plugin uses returns data on tv shows. It got two commands, tv and ep.
    tv uses episodeworld.com and ep uses tvrage.com.
    """
    threaded = True

    ######################
    # INTERNAL FUNCTIONS #
    ######################

    def _httpget(self, url, h=None, d=None, l=True):
        """General HTTP resource fetcher. Pass headers via h, data via d, and to log via l."""

        if self.registryValue('logURLs') and l:
            self.log.info(url)

        try:
            if h and d:
                page = utils.web.getUrl(url, headers=h, data=d)
            else:
                page = utils.web.getUrl(url)
            return page
        except utils.web.Error as e:
            self.log.error("ERROR opening {0} message: {1}".format(url, e))
            return None

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def movie(self, irc, msg, args, opttitle):
        """<title>

        Fetches IMDB information about a movie.
        Ex: Batman
        """


        url_params = {'r':'xml', 'plot':'full', 't':opttitle}
        url = "http://www.omdbapi.com/?%s" % (utils.web.urlencode(url_params))
        # fetch xml.
        html = self._httpget(url)
        if not url:
            irc.reply("ERROR fetching {0}".format(url))
            return
        # process xml.
        xml = ElementTree.fromstring(html)
        # iterate.
        for node in xml.iter('root'):
            if node.get('response') == 'False':
                irc.reply("Sorry, I could not find '{0}' in the IMDB DB.".format(opttitle))
                return
        # no errors so spitout.
        for movie in xml.findall('movie'):
            irc.reply("{0} ({1}) || {2} || {3} || {4}".format(movie.get('title').encode('utf-8'),
                                                                                  movie.get('year').encode('utf-8'),
                                                                                  movie.get('runtime').encode('utf-8'),
                                                                                  movie.get('imdbRating').encode('utf-8'),
                                                                                  movie.get('imdbID').encode('utf-8')))
            irc.reply("Director: {0} || Actors: {1}".format(movie.get('director').encode('utf-8'),
                                                                                movie.get('actors').encode('utf-8')))

            irc.reply("{0}".format(movie.get('plot').encode('utf-8')))

    movie = wrap(movie, [('text')])

    def ep(self, irc, msg, args, opttitle):
        """<title>

        Returns date and name of previous and next episode of the given series.
        Ex: Burn Notice
        """

        url = "http://www.episodeworld.com/botsearch/%s" % (utils.web.urlquote(opttitle))
        html = self._httpget(url)
        if not url:
            irc.reply("ERROR fetching {0}".format(url))
            return
        # process what we get back.
        epitems = html.split('<br>\n')
        # output
        irc.reply("{0} :: {1} :: {2}".format(epitems[0], epitems[1], epitems[2]))

    ep = wrap(ep, ['text'])

    def tv(self, irc, msg, args, opttitle):
        """<title>

        Returns information about the given series.
        Ex: Burn Notice
        """

        url = "http://services.tvrage.com/tools/quickinfo.php?show=%s" % (utils.web.urlquote(opttitle))
        html = self._httpget(url)
        if not url:
            irc.reply("ERROR fetching {0}".format(url))
            return

        if 'No Show Results Were Found' in html:
           irc.reply("Sorry, I didn't find anything for '{0}' on tvrage.com".format(opttitle))
           return

        # Remove <pre> at the start
        html = html[5:]
        html = html.splitlines()
        """
        Example of what is returned (after removing "<pre>")

        Show ID@15343
        Show Name@Stargate Universe
        Show URL@http://www.tvrage.com/Stargate_Universe
        Premiered@2009
        Started@Oct/02/2009
        Ended@
        Latest Episode@01x18^Subversion^May/21/2010
        Next Episode@01x19^Incursion (1)^Jun/04/2010
        RFC3339@2010-06-04T21:00:00-4:00
        GMT+0 NODST@1275692400
        Country@USA
        Status@New Series
        Classification@Scripted
        Genres@Sci-Fi
        Network@Syfy
        Airtime@Friday at 09:00 pm
        Runtime@60
        """
        """Different possible replies:

        No show with that name found (what. this shouldn't really happen).

        [ Showname ] - Stargate Universe [ Status ] - New Series
        [ Next Ep ] - 01x19^Incursion (1)^Jun/04/2010 [ Airtime ] - Friday at 09:00 pm
        [ Genres ] - Sci-Fi [ URL ] - http://www.tvrage.com/Stargate_Universe

        [ Showname ] - Chuck [ Status ] - Returning Series
        [ Genres ] - Action | Comedy | Drama [ URL ] - http://www.tvrage.com/Chuck

        [ Showname ] - Star Trek: The Next Generation [ Status ] - Canceled/Ended
        [ Started ] - Sep/28/1987 [ Ended ] - May/23/1994
        [ Genres ] - Action | Adventure | Sci-Fi [ URL ] - http://www.tvrage.com/Star_Trek-The_Next_Generation

        """
        dict = {}
        for line in html:
            line = line.strip() # Just to be sure.
            head, sep, tail = line.partition("@")
            dict[head] = tail
        # dict should at this point contain "Show Name": "Stargate Universe" etc etc.
        # Since there is a bit of info we try to spread it over 3 lines.
        firstline = ""
        if("Show Name" in dict):
            firstline += " [ Showname ] - " + dict["Show Name"]
        else:
            irc.reply("No show with that name found (what. this shouldn't really happen).")
            return
        if("Status" in dict):
            firstline += " [ Status ] - " + dict["Status"]
        irc.reply(firstline.strip()) # Uses strip just to be consistent with the other lines.

        # Note: second line never happens for shows that are still running, but next date is unknown.
        secline = ""
        if("Next Episode" in dict):
            secline += " [ Next Ep ] - " + dict["Next Episode"].replace('^', ' - ')
            # No point in adding airtime if we don't know what date the episode will be anyway.
            if("Airtime" in dict):
                secline += " [ Airtime ] - " + dict["Airtime"]
        elif("Started" in dict and "Ended" in dict):
            # Also want to make sure we actually have an enddate.
            # Checking for startsdate aswell, for fun.
            if(dict["Started"] and dict["Ended"]):
                secline += " [ Started ] - " + dict["Started"]
                secline += " [ Ended ] - " + dict["Ended"]
        # if("Country" in dict):
        #     secline += " [ Country ] - " + dict["Country"]
        if(secline):
            irc.reply(secline.strip()) # As we are not sure what line comes first all have a space in front of them.

        thirdline = ""
        if("Genres" in dict):
            thirdline += " [ Genres ] - " + dict["Genres"]
        # if("Classification" in dict):
        #     thirdline += " [ Class ] - " + dict["Classification"]
        if("Show URL" in dict):
            thirdline += " [ URL ] - " + dict["Show URL"]
        # if("Network" in dict):
        #     thirdline += " [ Network ] - " + dict["Network"]
        if(thirdline):
            irc.reply(thirdline.strip())
    tv = wrap(tv, ['text'])

Class = Series


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
