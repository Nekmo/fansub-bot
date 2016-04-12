try:
    from secrets import *
except ImportError:
    pass


PROTOCOLS = [
    # 'telegram',
    'irc',
]

PLUGINS = [
    # 'hello',
    'bot',
    'random',
    # 'test',
    'release',
    'premux',
    'commands',
    'fansub_conf',
    'patch',
]