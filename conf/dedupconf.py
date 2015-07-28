# -*- encoding: utf-8 -*-
import simstring

# Configurações do simstring para busca de títulos similares

titleNGram = 5   # Tamanho dos n-grams utilizados na geração do índice
titleBE = False  # Inserir marcas especiais para começo e fim de strings nos n-grams?
titleMeasure = simstring.jaccard  # Métrica de similaridade
titleThreshold = 0.7              # Limiar de similaridade

# Para os autores, é realizada uma comparação bastante conservativa
# (vide algoritmo em nameutil.AuthorSet). Assume-se que algum dos proprietários
# de CV pode ter esquecido de digitar o nome de alguns coautores, ou que possa ter
# digitado em uma ordem incorreta. Se a distância de edição normalizada pelo
# tamanho dos nomes e pelo número de nomes for acima do limiar definido abaixo,
# as produções correspondentes não são consideradas duplicatas.
authorThreshold = 0.9

# Define se as produções precisam ter sido publicadas no mesmo ano para serem
# consideradas duplicatas
ensurePublishedSameYear = True
