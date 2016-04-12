# coding=utf-8
import json
import os
from fields import DirMultiplesRoots
from nekbot import settings
from nekbot.core.commands import command
from nekbot.core.exceptions import InvalidArgument

__author__ = 'nekmo'


def get_config_path(tvshow):
    config_path = os.path.join(tvshow, 'config.json')
    return config_path


def get_data(config_path):
    if os.path.exists(config_path):
        data = json.load(open(config_path, 'rb'))
    else:
        data = {}
    return data


@command('fansub-conf', DirMultiplesRoots(settings.OWN_WORK_DIRECTORY, settings.FOREIGN_WORK_DIRECTORY))
def fansub_conf(msg, tvshow, key, value):
    config_path = get_config_path(tvshow)
    data = get_data(config_path)
    if data.get(key):
        msg.reply('Updating value for key %s: "%s" -> "%s"' % (key, data[key], value))
    else:
        msg.reply('Creating key %s' % key)
    if value in ['None', 'True', 'False'] or value.isdigit():
        value = eval(value)
    data[key] = value
    json.dump(data, open(config_path, 'wb'))


@command('fansub-conf-del', DirMultiplesRoots(settings.OWN_WORK_DIRECTORY, settings.FOREIGN_WORK_DIRECTORY))
def fansub_conf_del(msg, tvshow, key):
    config_path = get_config_path(tvshow)
    data = get_data(config_path)
    if not data.get(key):
        raise InvalidArgument('The key is not valid. It does not exists.', key)
    del data[key]
    json.dump(data, open(config_path, 'wb'))
    return 'Key %s deleted.' % key
