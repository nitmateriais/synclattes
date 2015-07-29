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
