# -*- coding: utf-8 -*-
import requests
from jasper import plugin


class WitAIPlugin(plugin.SpeechHandlerPlugin):
    def get_priority(self):
        return 50

    def get_phrases(self):
        return [
            self.gettext("WITAI"),
            self.gettext("PLAYING")]

    def handle(self, text, mic, json):
        """
            Handles the witai response if there are intents attached.
        """

        json = json[1]
        if json.get('outcomes'):
            for outcome in json['outcomes']:
                if outcome['intent'] == 'who_is_playing_on_steam':
                    r = requests.get(
                            'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/V0002/?key=2DF0CC2B874FC8791DE89EEFDA69B664&steamids=76561198045363986,76561198045146840,76561198278731872')
                    try:
                        r.raise_for_status()
                        response = r.json()

                    except requests.exceptions.HTTPError:
                        self._logger.critical('Request failed with response: %r',
                                              r.text,
                                              exc_info=True)
                        return []
                    except requests.exceptions.RequestException:
                        self._logger.critical('Request failed.', exc_info=True)
                        return []
                    except ValueError as e:
                        self._logger.critical('Cannot parse response: %s',
                                              e.args[0])
                        return []
                    except KeyError:
                        self._logger.critical('Cannot parse response.',
                                              exc_info=True)
                        return []
                    else:
                        nowPlaying = {}
                        for player in response['response']['players']:
                            if player.get('gameextrainfo'):
                                nowPlaying[player['realname']] = player['gameextrainfo']
                        if not nowPlaying:
                            mic.say("No one is playing right now.")
                        else:
                            if nowPlaying['Michael Beck'] and (len(nowPlaying.keys()) is 1):
                                mic.say("You are the only one playing.")
                            else:
                                for name in nowPlaying.keys():
                                    if name is not 'Michael Beck':
                                        mic.say("%r is playing %r", name, nowPlaying[name])

    def is_valid(self, text):
        """
            Returns True if the text is related to witai.

            Arguments:
            text -- user-input, typically transcribed speech
        """

        text = text.upper()
        return self.gettext('witai').upper() in text
