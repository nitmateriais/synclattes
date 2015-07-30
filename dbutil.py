# -*- encoding: utf-8 -*-
from sqlalchemy import or_
import db

def yieldNotYetSyncedRevisions(q, **kwargs):
    """
    Percorre batches de last_revision que ainda não tenham sido sincronizados.

    - `q`: query que deve conter um join nas tabelas last_revision e item.
    - `id_from_row`: função para obter o item_id a partir da projeção, caso o
      resultado não esteja sendo coletado em um objeto ORM.
    """
    return db.yield_batches(q.filter(db.Item.dspace_cur_rev_id
                                     .op('is distinct from')
                                     (db.LastRevision.id)),
                            db.LastRevision.item_id, **kwargs)

def filterDupLastRevGroup(q, rev):
    """ Filtra a query `q` para o grupo de duplicatas da revisão `rev` """
    return q.filter(or_(
        db.LastRevision.id == rev.id,
        db.LastRevision.id == rev.duplicate_of_id,
        db.LastRevision.duplicate_of_id == rev.id))


"""
-- Operação realizada por RevGroupVisitor e splitMainRev em SQL puro
--
select main_id, other_revs from
(
    select o.id as main_id, array(select i.id from synclattes.last_revision i where i.duplicate_of_id = o.id) as other_revs
        from synclattes.last_revision o
    where o.duplicate_of_id is null
        and o.meta is not null
) t
where array_length(other_revs, 1) > 0
and exists (
    select 1
      from synclattes.last_revision
      join synclattes.item on last_revision.item_id = item.id
    where last_revision.id = any (array_append(other_revs, main_id))
      and item.dspace_cur_rev_id is distinct from last_revision.id)
"""

class RevGroupVisitor(object):
    def __init__(self):
        self.visitedRevIds = set()

    def getRevGroup(self, rev):
        if rev.id in self.visitedRevIds:
            return []
        rev_group = filterDupLastRevGroup(db.session.query(db.LastRevision), rev).all()
        for r in rev_group:
            if r.id in self.visitedRevIds:
                return []
            self.visitedRevIds.add(r.id)
        return rev_group

    def yieldGroups(self):
        q = db.session.query(db.LastRevision)\
                      .join(db.LastRevision.item)\
                      .filter(db.LastRevision.meta.isnot(None))
        for rev in yieldNotYetSyncedRevisions(q, batch_size=256):
            rev_group = self.getRevGroup(rev)
            if len(rev_group) < 2:  # 0 - grupo já visitado
                continue            # 1 - revisão sem duplicatas
            yield rev_group

def splitMainRev(rev_group):
    mainRev = None
    otherRevs = []
    for rev in rev_group:
        if rev.duplicate_of_id is None:
            mainRev = rev
        else:
            otherRevs.append(rev)
    if mainRev is None:
        raise ValueError('Não foi passado um grupo completo')
    return mainRev, otherRevs

def reassignRevGroup(revisions, mainId):
    # Modifica o campo de todas as revisões, exceto a principal,
    # e de quaisquer revisões que já forem duplicatas das mesmas
    revIds = set(rev.id for rev in revisions) - {mainId,}
    db.session.query(db.Revision) \
        .filter(or_(db.Revision.id.in_(revIds),
                    db.Revision.duplicate_of_id.in_(revIds))) \
        .update({db.Revision.duplicate_of_id: mainId},
                synchronize_session=False)
    # Assegura que a principal tenha o campo nulo
    db.session.query(db.Revision) \
        .filter(db.Revision.id == mainId) \
        .update({db.Revision.duplicate_of_id: None},
                synchronize_session=False)
    db.session.commit()

def checkGroupIntegrity():
    """ Verifica se todos os grupos então com duplicate_of_id uniforme """
    return db.session.query(db.func.count())\
                     .filter(db.Revision.id.in_(db.session.query(db.Revision.duplicate_of_id)))\
                     .filter(db.Revision.duplicate_of_id.isnot(None))\
                     .scalar() == 0
