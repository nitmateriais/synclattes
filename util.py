# -*- encoding: utf-8 -*-
import re, unicodedata
import lxml.html
import conf.wsconf as wsconf
import logging

def onlyNumbers(s):
    """ Remove caracteres não-numéricos da string """
    return re.sub(r'[^\d]', '', s)

def norm(s, encoding=wsconf.serverEncoding):
    """ Retira acentos e espaços sobrando, e transforma tudo em minúsculas """
    if not isinstance(s, unicode):
        s = s.decode(encoding)
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')\
        .encode('ascii','ignore')\
        .strip()\
        .lower()
    return re.sub(r'\s+', ' ', s)

def decodeHtml(s, encoding=wsconf.serverEncoding):
    """ Decodifica a string como HTML de forma permissiva """
    if s is None:
        return None
    if not isinstance(s, unicode):
        s = s.decode(encoding)
    try:
        return lxml.html.document_fromstring(s).text_content()\
               .replace(u'\xa0', u' ') # converte '&nbsp;' para espaço comum
    except:
        return s

class HtmlValuesElementWrapper(object):
    """
    O XML do CV Lattes codifica entities XML duas vezes porque o contéudo dos campos
    é, na verdade, HTML. Dessa forma, um caractere `&`, por exemplo, vira `&amp;amp;`.
    Além disso, em alguns casos os campos chegam a conter tags, por exemplo `<b>`.
    Esta classe é um wrapper sobre a classe Element da biblioteca lxml que torna a
    decodificação do HTML interno dos campos transparente para o programador.
    """
    def __init__(self, element):
        self.element = element
    def xpath(self, *args, **kwargs):
        results = []
        for result in self.element.xpath(*args, **kwargs):
            results.append(HtmlValuesElementWrapper(result))
        return results
    def items(self, *args, **kwargs):
        results = []
        for k, v in self.element.items(*args, **kwargs):
            results.append((k, decodeHtml(v)))
        return results
    def get(self, *args, **kwargs):
        return decodeHtml(self.element.get(*args, **kwargs))
    def getText(self):
        return decodeHtml(self.element.text)
    def setText(self, value):
        self.element.text = value
    text = property(getText, setText)
    def getTag(self):
        return self.element.tag
    def setTag(self, value):
        self.element.tag = value
    tag = property(getTag, setTag)

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

def firstOrNone(a):
    if a is not None:
        for x in a:
            return x
    return None

def maybeBind(f, value):
    """ Operador de bind no monad Maybe, onde Nothing é representado por None """
    if value is None:
        return None
    return f(value)
