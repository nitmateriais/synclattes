# -*- encoding: utf-8 -*-
import re, unicodedata

def onlyNumbers(s):
    """ Remove caracteres não-numéricos da string """
    return re.sub(r'[^\d]', '', s)

def norm(s, encoding='iso-8859-1'):
    """ Retira acentos e espaços sobrando, e transforma tudo em minúsculas """
    if not isinstance(s, unicode):
        s = s.decode(encoding)
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
               if unicodedata.category(c) != 'Mn')\
        .encode('ascii','ignore')\
        .strip()\
        .lower()
    return re.sub(r'\s+', ' ', s)

def singleTag(tagList):
    """ Obtém a tag de uma lista que, supõe-se, contém uma única tag """
    if len(tagList) != 1:
        raise ValueError('len(%s) != 1' % repr(tagList))
    return tagList[0]

def noneIfEmpty(s):
    """ Transforma string vazia em None """
    if s == '':
        return None
    return s

def maybeBind(f, value):
    """ Operador de bind no monad Maybe, onde Nothing é representado por None """
    if value is None:
        return None
    return f(value)
