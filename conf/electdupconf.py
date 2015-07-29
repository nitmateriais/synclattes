# -*- encoding: utf-8 -*-

# Pontuação devido ao vínculo do proprietário do CV
scoreForRole = {
    u"Professor Ensino Superior": 1000,
    u"Técnico-Administrativo": 1000,
    u"Aposentado": 1000,
    u"Procurador": 1000,
    u"Professor Ensino Superior Substituto/Temporário/Visitante": 900,
    u"Pesquisador - Pós-Doutorado": 900,
    u"Aluno de Pós-Graduação - Doutorado": 200,
    u"Aluno de Pós-Graduação - Mestrado": 100,
}

# Pontuação por ter um DOI definido nos metados
scoreDoi = 500

# Pontuação para cada autor com ID de autoridade definido
scorePerAuthorWithAuthorityId = 50

# Pontuação para flag de relevância
scoreForRelevanceFlag = 10

# Pontuação para cada tipo diferente de metadado encontrado no registro
scorePerMetadatumKey = 1
