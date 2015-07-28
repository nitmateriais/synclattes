# -*- encoding: utf-8 -*-
import re, util
from collections import namedtuple

nobiliaryParticles = {'de','dit','la','von','af','der','und','zu','of'}
nobiliaryRegex = re.compile('|'.join(r'\b%s\b'%word for word in nobiliaryParticles))

def nameReorder(name):
    """ Reordena "sobrenome, nome" -> "nome sobrenome" """
    if ',' in name:
        return ' '.join(reversed(name.split(',', 2)))
    return name

def initials(name):
    """ Obtém as iniciais de um nome normalizadas """
    name = util.norm(name)
    # Retira partículas e reordena
    name = nameReorder(nobiliaryRegex.sub(' ', name))
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


class AuthorSet(list):
    Author = namedtuple('Author', ['id', 'cn', 'fn'])
    def compare(self, other):
        """
        Comparação heurística, gulosa e tolerante entre conjuntos de autores

        Retorna uma distância normalizada. Quanto menor a distância,
        mais similares os conjuntos.
        """
        # Encontra IDs de autoridade que estejam em ambos os conjuntos
        a, b = (set(x.id for x in xs) for xs in (self, other))
        commonIds = a.intersection(b) - {None,}
        # Tenta uma comparação entre nomes usando cada um dos campos
        # de nome (cn - nome em citações, fn - nome completo)
        results = []
        for f in (lambda x:x.cn, lambda x:x.fn):
            # Obtém duas listas de nomes, excluindo os que possuem IDs
            # de autoridade em comum
            a, b = ([util.norm(nameReorder(f(x)), util.NormLevel.ONLY_LETTERS)
                     for x in xs if x.id not in commonIds]
                    for xs in (self, other))
            results.append(self._compareNames(a, b))
        return min(results) / min(len(self), len(other))
    @staticmethod
    def _compareNames(a, b):
        # Garante que não existem nomes vazios nos conjuntos
        a = [x for x in a if len(x) > 0]
        b = [y for y in b if len(y) > 0]
        # Garante que o primeiro conjunto seja o menor
        if len(a) > len(b):
            a, b = b, a
        # Se já o primeiro conjunto for vazio (pode ter sido zerado
        # via ID de autoridade), considera distância zero
        if len(a) == 0:
            return 0.
        # Para cada nome do primeiro conjunto, retira os nomes mais
        # similares do segundo conjunto (algoritmo guloso)
        totalDist = 0.
        for x in a:
            minDist, idxB = min((levenshtein(x,y),i) for i,y in enumerate(b))
            y = b.pop(idxB)
            totalDist += float(minDist) / min(len(y), len(x))
        return totalDist
    @staticmethod
    def toAuthor(metadatum):
        return AuthorSet.Author(fn=metadatum.get('_nomecompleto'),
                                cn=metadatum.get('value'),
                                id=metadatum.get('authority'))
    @staticmethod
    def toAuthorSet(metadata):
        return AuthorSet([AuthorSet.toAuthor(x) for x in metadata])