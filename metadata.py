# -*- encoding: utf-8 -*-
from lxml.builder import ElementMaker

class CF:
    """ Confidence values """
    ACCEPTED = 600
    UNCERTAIN = 500
    AMBIGUOUS = 400
    NOTFOUND = 300
    FAILED = 200
    REJECTED = 100
    NOVALUE = 0
    UNSET = -1

class JSONMetadataBuilder(object):
    def __init__(self, meta={}):
        self.meta = dict(meta)
    def add(self, mdschema='dc', element=None, qualifier=None, lang=None, authority=None, confidence=None, value=None, **kwargs):
        if mdschema is None or element is None:
            raise ValueError('Nor mdschema nor element can be null')
        datum = dict(kwargs)
        datum['value'] = value
        if lang is not None:
            datum['lang'] = lang
        if authority is not None:
            datum['authority'] = authority
        if confidence is not None:
            datum['confidence'] = confidence
        self.meta\
            .setdefault(mdschema, {})\
            .setdefault(element, {})\
            .setdefault(qualifier, [])\
            .append(datum)
        return self
    def build(self):
        return self.meta

def jsonToXml(json):
    nsmap = {'atom': 'http://www.w3.org/2005/Atom',
             'dim':  'http://www.dspace.org/xmlns/dspace/dim'}
    atom = ElementMaker(namespace=nsmap['atom'], nsmap=nsmap)
    dim  = ElementMaker(namespace=nsmap['dim'],  nsmap=nsmap)
    fields = []
    assert(isinstance(json, dict))
    for mdschema, elements in json.iteritems():
        assert(isinstance(elements, dict))
        for element, qualifiers in elements.iteritems():
            assert(isinstance(qualifiers, dict))
            for qualifier, metadata in qualifiers.iteritems():
                assert(isinstance(metadata, list))
                for metadatum in metadata:
                    assert(isinstance(metadatum, dict))
                    value = metadatum.get('value')
                    attr = {k:str(v) for k,v in metadatum.iteritems()
                            if k != 'value' and not k.startswith('_') and v is not None}
                    attr['mdschema'] = mdschema
                    attr['element'] = element
                    if qualifier is not None:
                        attr['qualifier'] = qualifier
                    fields.append(dim.field(value, **attr))
    return atom.entry(*fields)
