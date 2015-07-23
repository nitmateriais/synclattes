from sqlalchemy import or_, and_
import db

class PessoaInstituicao(object):
    def __init__(self, entidade):
        self.entidade = entidade
    @staticmethod
    def fromIdentificador(cpfOrNumeroUFSCar):
        return PessoaInstituicao(db.session.query(db.Pessoa).filter(or_(
                   db.Pessoa.cpf == cpfOrNumeroUFSCar,
                   db.Pessoa.id  == cpfOrNumeroUFSCar
               )).one())
    def getEntidade(self):
        """ Entidade a ser inserida na chave estrangeira de PessoaLattes """
        return self.entidade
    def getCpf(self):
        return self.entidade.cpf
    def getPessoaLattes(self):
        return self.entidade.pessoa_lattes
