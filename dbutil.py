# -*- encoding: utf-8 -*-
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
