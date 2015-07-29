# -*- encoding: utf-8 -*-
import re
from lxml.builder import ElementMaker
import doiutil, util

class CF:
    """ Valores canônicos de confiança """
    ACCEPTED = 600
    UNCERTAIN = 500
    AMBIGUOUS = 400
    NOTFOUND = 300
    FAILED = 200
    REJECTED = 100
    NOVALUE = 0
    UNSET = -1

# Formato de um metadado em JSON:
# { "`mdschema`": { "`element`": {"`qualifier`": [ {"value": "`value`", "attr": "`attr`" } ] }}}
#
# Observações:
#  * Valores de `qualifier` vazios são sempre armazenado como strings vazias (""). Não é
#    possível utilizar None, pois valores nulos não são permitidos como chave de
#    dicionários na especificação do JSON.
#  * Valores de `mdschema` iniciados em `_` são ignorados na conversão para XML.
#  * Valores de `attr` iniciados em `_` são ignorados na conversão para XML.
#
# Formato do metadado após conversão para XML:
# <dim:field mdschema="`mdschema`"
#            element="`element`"
#            qualifier="`qualifier`"
#            attr="`attr`">
# `value`
# </dim:field>
#
class JSONMetadataBuilder(object):
    def __init__(self):
        self.meta = {}
        self.shadow = {}  # cópia sombra em sets, para eliminação de metadados duplicados
    def add(self, mdschema='dc', element=None, qualifier=None, lang=None, authority=None, confidence=None, value=None, **kwargs):
        """
        Adiciona um metadado

        - `mdschema`: Esquema do metadado, por padrão "dc" (dublin core).
        - `element`: Nome do elemento (obrigatório).
        - `qualifier`: Qualificador (opcional).
        - `lang`: Idioma no qual o valor está escrito, no formato ISO639-2 (opcional).
        - `authority`: Identificador de autoridade para o valor (opcional).
        - `confidence`: Grau de confiança no identificador de autoridade (opcional).
          Recomenda-se utilizar algum dos valores fornecidos na classe `CF`.
        - `value`: Valor do metadado (obrigatório). Caso vazio, a chamada a
          este método é ignorada.

        Caso `mdschema` comece com um underline, o metadado é armazenado, mas é
        ignorado como um todo ao ser sincronizado com o DSpace.

        Atributos adicionais, além dos listados acima, também podem ser fornecidos.
        O nome dos atributos adicionais deve começar com um underline para que eles
        não sejam sincronizados com o DSpace. Nesse caso, o restante do metadado é
        sincronizado, sendo omitidos apenas os parâmetros que iniciem com underline.
        """
        if mdschema is None or element is None:
            raise ValueError('Nor mdschema nor element can be null')
        if util.noneIfEmpty(value) is None:
            return
        qualifier = qualifier or ''
        datum = dict(kwargs)
        datum['value'] = value
        if lang is not None:
            datum['lang'] = lang
        if authority is not None:
            datum['authority'] = authority
        if confidence is not None:
            datum['confidence'] = confidence
        # Verifica se já existe no conjunto de metadados com o mesmo valor e mesma chave de autoridade
        if (value, authority) in self.shadow.get(mdschema, {}).get(element, {}).get(qualifier, set()):
            return self
        # Adiciona metadado (em uma lista, para preservar a ordem)
        self.meta\
            .setdefault(mdschema, {}).setdefault(element, {}).setdefault(qualifier, [])\
            .append(datum)
        # Adiciona cópia sombra em um set
        self.shadow\
            .setdefault(mdschema, {}).setdefault(element, {}).setdefault(qualifier, set())\
            .add((value, authority))
        return self
    def build(self):
        return self.meta

class JSONMetadataWrapper(object):
    def __init__(self, json):
        assert(isinstance(json, dict))
        self.json = json

    def get(self, k, what='value'):
        """
        Obtém metadados a partir de uma chave `k` no formato "dc.element.qualifier"
        """
        path = k.split('.', 3)
        meta = self.json
        for subk in path[:2]:
            meta = meta.get(subk, {})
        meta = meta.get(path[2] if len(path)==3 else '', [])
        if what is None:
            return meta
        return [datum.get(what) for datum in meta]

    def getSingle(self, k, what='value'):
        """
        Retorna o primeiro metadado encontrado com a chave `k`.
        """
        return util.firstOrNone(self.get(k, what='value'))

    def getDoi(self):
        return doiutil.filter(self.getSingle('dc.identifier.uri'))

    def getTitle(self):
        return self.getSingle('dc.title')

    def getType(self):
        return self.getSingle('dc.type')

    def getYear(self):
        dateIssued = self.getSingle('dc.date.issued')
        if dateIssued is None or not re.match(r'^\d{4}$', dateIssued):
            return None
        return dateIssued

    def iterMetadata(self):
        for mdschema, elements in self.json.iteritems():
            assert(isinstance(elements, dict))
            if mdschema.startswith('_'):
                continue
            for element, qualifiers in elements.iteritems():
                assert(isinstance(qualifiers, dict))
                for qualifier, metadata in qualifiers.iteritems():
                    assert(isinstance(metadata, list))
                    yield (mdschema, element, qualifier, metadata)

    def toXml(self):
        nsmap = {'atom': 'http://www.w3.org/2005/Atom',
                 'dim':  'http://www.dspace.org/xmlns/dspace/dim'}
        atom = ElementMaker(namespace=nsmap['atom'], nsmap=nsmap)
        dim  = ElementMaker(namespace=nsmap['dim'],  nsmap=nsmap)
        fields = []
        for mdschema, element, qualifier, metadata in self.iterMetadata():
            for metadatum in metadata:
                assert(isinstance(metadatum, dict))
                value = metadatum.get('value')
                attr = {k:str(v) for k,v in metadatum.iteritems()
                        if k != 'value' and not k.startswith('_') and v is not None}
                attr['mdschema'] = mdschema
                attr['element'] = element
                if qualifier != '':
                    attr['qualifier'] = qualifier
                fields.append(dim.field(value, **attr))
        return atom.entry(*fields)
