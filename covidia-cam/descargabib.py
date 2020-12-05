# -*- coding: utf-8 -*-

import datetime as dt
import os.path as pth
import requests
from shutil import copyfile


# ALWAYS_UPDATE_DEFAULT = False
ALWAYS_UPDATE_DEFAULT = True


def descarga(url, fn, isbinary=False, isascii=False, isbackup=False,
             prevpage=None, verify=True, always=ALWAYS_UPDATE_DEFAULT):
    today = dt.date.today()

    ret = True

    if pth.isfile(fn):
        modifiedTime = pth.getmtime(fn)
        changed = dt.datetime.fromtimestamp(modifiedTime).date()

        if isbackup:
            basename = pth.basename(fn)
            rootfn, ext = pth.splitext(basename)
            dirname = pth.dirname(fn)
            changedstr = str(changed)

            backupfn = pth.join(dirname, 'backup',
                                rootfn + '-' + changedstr + ext)
            print('Backup: {} -> {}'.format(fn, backupfn))
            copyfile(fn, backupfn)

    if not pth.isfile(fn) or changed != today or always:
        print('Descargando:', url)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}  # noqa: E501
        with requests.Session() as s:
            if prevpage:
                s.get(prevpage, headers=headers, verify=verify)
            r = s.get(url, headers=headers, verify=verify)
        if r.status_code == requests.codes.ok:
            if isbinary:
                with open(fn, 'wb') as fp:
                    fp.write(r.content)
            elif isascii:
                text = r.content.decode('ascii', 'ignore')
                with open(fn, 'w', encoding='utf-8') as fp:
                    fp.write(text.replace('\r\n', '\n'))
            else:
                with open(fn, 'w', encoding='utf-8') as fp:
                    fp.write(r.text.replace('\r\n', '\n'))
        else:
            print('ERROR', r.status_code, 'descargando:', fn)
            ret = False

    return ret
