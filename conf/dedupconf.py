# -*- encoding: utf-8 -*-
import simstring

# Configurações do simstring para busca de títulos similares

titleNGram = 5   # Tamanho dos n-grams utilizados na geração do índice
titleBE = False  # Inserir marcas especiais para começo e fim de strings nos n-grams?
titleMeasure = simstring.jaccard  # Métrica de similaridade
titleThreshold = 0.7              # Limiar de similaridade
