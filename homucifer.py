#!/usr/bin/env python3

"""A kick-happy Python IRC bot using pydle.
"""


from collections import OrderedDict
import datetime
import json
from random import randint
import sys
import pydle
import dateparser


BaseHomu = pydle.featurize(pydle.features.RFC1459Support,
                           pydle.features.ircv3.SASLSupport,
                           pydle.features.TLSSupport,
                           pydle.features.AccountSupport)


class HomuBot(BaseHomu):
    def __init__(self, channel, min_idle, *args, **kwargs):
        self.ns_sent_queries = OrderedDict()
        self.ns_queries = OrderedDict()
        self.ns_cache = dict()
        self.channel = channel
        self.min_idle = min_idle
        super().__init__(*args, **kwargs)

    def on_connect(self):
        self.join(self.channel)

    @pydle.coroutine
    def on_join(self, channel, user):
        if user != self.nickname:
            if user not in self.ns_cache:
                print('Checking time of ' + user)
                reg_time = yield self.check_reg_time(user)
                print('{} registered at {}'.format(user, reg_time))
                self.ns_cache[user] = dateparser.parse(date_string=reg_time,
                                                       languages=['en'])
            if (datetime.datetime.now(datetime.timezone.utc) -
                    self.ns_cache[user] < self.min_idle):
                print('{} needs to be kicked imho'.format(user))
                self.kick(channel, user, 'Incubators are not welcome here.')
            else:
                print('{} is alright'.format(user))

    def on_notice(self, target, by, message):
        if by == 'NickServ':
            TIME_STR = '  Time registered: '
            if message.startswith('  ') and len(self.ns_queries) > 0:
                last = next(reversed(self.ns_queries))
                if (message.startswith(TIME_STR) and last and
                        last != self.nickname):
                    self.ns_queries[last].set_result(
                        message.replace(TIME_STR, ""))
            elif not message.endswith("isn't registered"):
                query_nick, second = message.split()[:2]
                if second == "is":
                    self.ns_queries[query_nick] = \
                        self.ns_sent_queries[query_nick]

    @pydle.coroutine
    def check_reg_time(self, user):
        self.message("NickServ", "INFO " + user)
        time = yield self.get_reg_time_future(user).result()
        del self.ns_queries[user]
        del self.ns_sent_queries[user]
        return time

    @pydle.coroutine
    def get_reg_time_future(self, user):
        print("Adding {} to queue".format(user))
        self.ns_sent_queries[user] = pydle.Future()
        return self.ns_sent_queries[user]

    def on_private_message(self, by, message):
        if message.lower().startswith("register"):
            self.kickban(self.channel, by, "Reading comprehension")
        else:
            self.message(by, "https://files.catbox.moe/ksxbm8.png")

    def on_invite(self, channel, by):
        self.message(by, "I'm not signing another contract.")

    def on_kick(self, channel, target, by, reason=None):
        if self.is_same_nick(by, "Godoka"):
            if randint(1, 10) == 1:
                self.message(channel, "<3")


def main():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError as e:
        print('No config.json has been found, please create one')
        sys.exit(1)
    try:
        homuconf = {
            'channel': config['channel'],
            'nickname': config['nickname'],
            'sasl_username': config['nickname'],
            'sasl_password': config['password'],
            'min_idle': datetime.timedelta(days=config['minimum_days']),
            }
        connconf = {
            'hostname': config['network'],
            'port': config['port'],
            'tls': config['use_tls'],
            'tls_verify': config['verify_tls']
            }
    except KeyError as e:
        print('Your configuration file is missing the key \'{}\''
              .format(e.args[0]))
        sys.exit(1)
    h = HomuBot(**homuconf)
    h.connect(**connconf)
    h.handle_forever()


if __name__ == '__main__':
    main()
