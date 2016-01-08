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
import urllib
import json
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

        url = "http://api.tvmaze.com/singlesearch/shows?q=" + urllib.quote_plus(opttitle)

        response = urllib.urlopen(url)

        data = json.loads(response.read())

        show_name = data['name']

        next_url = data['_links']['nextepisode']['href']
        prev_url = data['_links']['previousepisode']['href']

        response_next = urllib.urlopen(next_url)
        data_next = json.loads(response_next.read())

        next_name = data_next['name']
        next_seas = data_next['season']
        next_num = data_next['number']
        next_date = data_next['airdate']

        response_prev = urllib.urlopen(prev_url)
        data_prev = json.loads(response_prev.read())

        previous_name = data_prev['name']
        previous_seas = data_prev['season']
        previous_num = data_prev['number']
        previous_date = data_prev['airdate']


        irc.reply(show_name)
        irc.reply("Previous: " + previous_date + " | S" + str(previous_seas) + "E" + str(previous_num) + " | " + previous_name)
        irc.reply("Next: " + next_date + " | S" + str(next_seas) + "E" + str(next_num) + " | " + next_name)

    ep = wrap(ep, ['text'])

    def tv(self, irc, msg, args, opttitle):
        """<title>

        Returns information about the given series.
        Ex: Burn Notice
        """

        url = "http://api.tvmaze.com/singlesearch/shows?q=" + urllib.quote_plus(opttitle)

        response = urllib.urlopen(url)

        data = json.loads(response.read())

        show_name = data['name']

        show_status = data['status']

        show_url = data['url']

        show_runtime= data['runtime']

        show_schedule = ', '.join(data['schedule']['days']) + " @ " + data['schedule']['time']

        show_genre = ''.join(data['genres'])

        show_network = data['network']['name']

        show_summary = data['summary']

        next_url = data['_links']['nextepisode']['href']

        response_next = urllib.urlopen(next_url)
        data_next = json.loads(response_next.read())

        next_name = data_next['name']
        next_seas = data_next['season']
        next_num = data_next['number']
        next_date = data_next['airdate']

        irc.reply(show_name + " (" + show_genre + ") " + "(" + show_status + ")")
        irc.reply(show_url)
        irc.reply("Schedule: " + show_schedule + " on " + show_network + " (" + str(show_runtime) + " minutes)")
        irc.reply("Next: " + next_date + " | S" + str(next_seas) + "E" + str(next_num) + " | " + next_name)
        irc.reply(show_summary)

    tv = wrap(tv, ['text'])

Class = Series


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
