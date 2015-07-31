# -*- encoding: utf-8 -*-
from sqlalchemy import select, exists, join, or_
from sqlalchemy.orm import aliased
from alchemyext.arraysel import ArraySel
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


def filterLastRevGroup(q, rev):
    """ Filtra a query `q` para o grupo de duplicatas da revisão `rev` """
    return q.filter(or_(
        db.LastRevision.id == rev.id,
        db.LastRevision.id == rev.duplicate_of_id,
        db.LastRevision.duplicate_of_id == rev.id))


def yieldRevIdGroups(excludeDeletedMeta=True, excludeSingleRevs=True, onlyGroupsPendingSync=True, batch_size=8192):
    LastRevMain = aliased(db.LastRevision, name='last_rev_main')
    LastRevOther = aliased(db.LastRevision, name='last_rev_other')

    q = db.session.query(LastRevMain.id.label('main_id'),
                         ArraySel(select([LastRevOther.id])
                                  .where(LastRevOther.duplicate_of_id == LastRevMain.id))
                         .label('other_revs'))\
                  .filter(LastRevMain.duplicate_of_id.is_(None))

    if excludeDeletedMeta:
        q = q.filter(LastRevMain.meta.isnot(None))

    q = q.subquery()
    outerq = db.session.query(q.c.main_id, q.c.other_revs)

    if excludeSingleRevs:
        outerq = outerq.filter(db.func.array_length(q.c.other_revs, 1) > 0)

    if onlyGroupsPendingSync:
        outerq = outerq.filter(
            exists(select([1])
                   .select_from(join(db.LastRevision, db.Item, db.LastRevision.item_id == db.Item.id))
                   .where(db.LastRevision.id ==
                          db.func.any(db.func.array_append(q.c.other_revs, q.c.main_id)))
                   .where(db.Item.dspace_cur_rev_id.op('is distinct from')(db.LastRevision.id))))

    return db.yield_batches(outerq, q.c.main_id, batch_size, id_from_row=lambda row:row[0])


def yieldRevGroups(**kwargs):
    for main_id, other_revs in yieldRevIdGroups(**kwargs):
        yield (db.session.query(db.Revision).filter(db.Revision.id == main_id).one(),
               db.session.query(db.Revision).filter(db.Revision.id.in_(other_revs)).all())


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
