# -*- encoding: utf-8 -*-
import re, unicodedata

def onlyNumbers(s):
    return re.sub(r'[^\d]', '', s)

def norm(s, encoding='iso-8859-1'):
    if not isinstance(s, unicode):
        s = s.decode(encoding)
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
               if unicodedata.category(c) != 'Mn')\
        .encode('ascii','ignore')\
        .strip()\
        .lower()
    return re.sub(r'\s+', ' ', s)

def singleTag(tagList):
    if len(tagList) != 1:
        raise ValueError('len(%s) != 1' % repr(tagList))
    return tagList[0]

def noneIfEmpty(s):
    if s == '':
        return None
    return s

def maybeBind(f, value):
    if value is None:
        return None
    return f(value)
