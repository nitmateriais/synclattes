# -*- encoding: utf-8 -*-
import itertools, logging

SCHEME = 'doi:'
RESOLVER = 'http://dx.doi.org'
OTHER_RESOLVERS = ['http://doi.acm.org']

logger = logging.getLogger('doiutil')

def toUrl(identifier):
    # Based on DSpace's org.dspace.identifier.DOI#DOIToExternalForm
    if identifier is None or identifier == '':
        return None
    if identifier.startswith(SCHEME):
        return RESOLVER + '/' + identifier[len(SCHEME):]
    if identifier.startswith('10.') and '/' in identifier:
        return RESOLVER + '/' + identifier
    for resolver in itertools.chain(OTHER_RESOLVERS, [RESOLVER]):
        if identifier.startswith(resolver + '/10.'):
            return RESOLVER + identifier[len(resolver):]
    logger.warning('Ignorando DOI inválido: %r', identifier)
    return None

def fromUrl(identifier):
    url = toUrl(identifier)
    if url is None:
        return None
    return url[len(RESOLVER)+1:]