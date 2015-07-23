from sqlalchemy import or_, and_
import db

def getPessoa(cpfOrNumeroUFSCar):
    return db.session.query(db.Pessoa).filter(or_(
               db.Pessoa.cpf == cpfOrNumeroUFSCar,
               db.Pessoa.id  == cpfOrNumeroUFSCar
           )).one()
