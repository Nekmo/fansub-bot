# coding=utf-8
from logging import getLogger
import os
import requests
import re
from nekbot import settings
from webscraping import xpath
from share.torrent import get_torrent_file

logger = getLogger('utils.nyaa')

URL_LOGIN = "https://www.nyaa.se/?page=%s"
URL_SUCCESS = "https://www.nyaa.se/?page=view&tid=%s"


class NyaaException(Exception):
    pass


def upload_to_nyaa(torrent_file, url_info, description):
    req = requests.Session()
    url = URL_LOGIN
    login_url = url % "login"
    data_login = dict(login=settings.NYAA_USER, password=settings.NYAA_PASSWORD, method=1, submit="Submit")
    res = req.post(login_url, data=data_login)

    if res.status_code != 200:
        raise NyaaException("status code error %s" % res.status_code)

    if "Login failed" in res.text:
        raise NyaaException("login failed")

    if "id" not in res.cookies and "pw" not in res.cookies:
        raise NyaaException("login cookies not set")

    upload_url = url % "upload"

    desc = description  # % dict(anime=anime, episodio=episodio)

    data = {"catid": "1_38",
            "info": url_info, "description": desc, "rules": 1,
            'submit': "Upload", "remake": "0", "anonymous": "0", "hidden": "1"}
    files = {'torrent': open(torrent_file, "rb")}
    res = req.post(upload_url, data, files=files)
    res_text = res.text
    if "Upload failed" in res_text:
        error = xpath.get(res_text, "//[@class='error']/text()")
        return NyaaException(error)

    reg = re.compile('tid=([\d].+?)\">View your torrent.')
    match = reg.search(res.text)
    if match:
        r = match.groups()[0]
        url = URL_SUCCESS % r
        return url
    return True


def nyaa(msg, paths):
    url_info = settings.NYAA_URL_INFO if not hasattr(settings.NYAA_URL_INFO, '__call__')\
        else settings.NYAA_URL_INFO(paths[0])
    description = settings.NYAA_DESCRIPTION if not hasattr(settings.NYAA_DESCRIPTION, '__call__')\
        else settings.NYAA_DESCRIPTION(paths[0])
    torrent_file = get_torrent_file(paths)
    if not os.path.exists(torrent_file):
        raise Exception('No existe el archivo .torrent. ¿Has puesto "torrent" en SHARE_VIDEO?')
    url = upload_to_nyaa(torrent_file, url_info, description)
    if url is not True:
        return url