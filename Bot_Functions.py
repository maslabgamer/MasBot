# 'Samuel'
import re

def parse_time(t):
    t = str(t).split('.')[0].split(':')
    time_m = ""
    if ',' in t[0]:
        days = t[0].split(',')
        t[0] = days[1].strip()
        if int(days[0].split(' ')[0]) > 0:
            time_m += "{0} days, ".format(days)
    for i, v in enumerate(t):
        t[i] = int(v)
    if t[0] > 0:
        time_m += "{0} hours, ".format(t[0])
    if t[1] > 0:
        time_m += "{0} minutes, ".format(t[1])
    if len(time_m) > 0:
        time_m += "and "
    return time_m + "{0} seconds ago.".format((t[2]))

def extract_affirmation(l):
    m = re.search('add affirmation: "(.+?)"', l)
    if m:
        return str(m.group(1))
    else:
        return None

def get_users(l):
    c = ""
    for chan in self.irc_channel:
        if chan in l.lower():
            c = chan
    l = l.split('353')[1].split(':')[1].split(' ')
    for i, v in enumerate(l):
        v = v if v[0].isalpha() else v[1:]
        l[i] = v if '\r\n' not in v[-2:] else v[:-2]
    if 'MasBot' in l:
        l.remove('MasBot')
    return l