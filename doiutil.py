# -*- encoding: utf-8 -*-
import logging

SCHEME = 'doi:'
RESOLVER = 'http://dx.doi.org'

logger = logging.getLogger('doiutil')

def toUrl(identifier):
    # Based on DSpace's org.dspace.identifier.DOI#DOIToExternalForm
    if identifier is None or identifier == '':
        return None
    if identifier.startswith(SCHEME):
        return RESOLVER + '/' + identifier[len(SCHEME):]
    if identifier.startswith('10.') and '/' in identifier:
        return RESOLVER + '/' + identifier
    if identifier.startswith(RESOLVER + '/10.'):
        return identifier
    logger.warning(u'Ignorando DOI inválido: %r', identifier)
    return None
