# -*- encoding: utf-8 -*-
import re, util

nobiliaryParticles = {'de','dit','la','von','af','der','und','zu','of'}
nobiliaryRegex = re.compile('|'.join(r'\b%s\b'%word for word in nobiliaryParticles))

def initials(name):
    """ Obtém as iniciais de um nome normalizadas """
    name = util.norm(name)
    # Retira partículas
    name = nobiliaryRegex.sub(' ', name)
    if ',' in name:
        # Reordena "sobrenome, nome" -> "nome sobrenome"
        name = ' '.join(reversed(name.split(',', 2)))
    # Separa nomes por espaços ou pontos, e junta apenas as iniciais
    name = ''.join([word[:1] for word in re.split(r'[\s.]+', name)])
    return re.sub(r'[^a-z]', '', name)

def dist(a, b):
    """ Distância de edição entre as inicias dos nomes `a` e `b` """
    return levenshtein(initials(a), initials(b))

def levenshtein(a, b):
    """ Distância de edição entre `a` e `b` """
    # http://hetland.org/coding/python/levenshtein.py
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]
