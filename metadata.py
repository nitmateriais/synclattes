# -*- encoding: utf-8 -*-

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

def jsondatum(mdschema='dc', element=None, qualifier=None, lang=None, authority=None, confidence=None, value=None):
    if mdschema is None or element is None:
        raise ValueError('Nem mdschema nem element podem ser nulos')
    datum = {'mdschema':mdschema, 'element':element, 'value': value}
    if qualifier is not None:
        datum['qualifier'] = qualifier
    if lang is not None:
        datum['lang'] = lang
    if authority is not None:
        datum['authority'] = authority
    if confidence is not None:
        datum['confidence'] = confidence
    return datum
