# -*- encoding: utf-8 -*-
import time, traceback, base64, io, zipfile
import suds, suds.client
from lxml import etree
import conf.wsconf as wsconf
import util


class Retry(object):
    def __init__(decorator, times=3, sleeptime=2.0):
        decorator.times = times
        decorator.sleeptime = sleeptime
    def __call__(decorator, func):
        def newFunc(*args, **kwargs):
            for i in xrange(decorator.times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    lasterr = e
                    traceback.print_exc(e)
                    time.sleep(decorator.sleeptime)
            raise lasterr
        return newFunc


class WSCurriculo(suds.client.Client):
    def __init__(self):
        suds.client.Client.__init__(self, wsconf.WSCurriculoUrl)

    @Retry()
    def obterCV(self, idCNPq):
        b64 = self.service.getCurriculoCompactado(id=idCNPq)
        if b64 is None:
            return None
        xmlz = zipfile.ZipFile(io.BytesIO(base64.b64decode(b64)))
        xml = xmlz.read(xmlz.namelist()[0])
        return util.HtmlValuesElementWrapper(etree.fromstring(xml))

    @Retry()
    def obterIdCNPq(self, *args):
        """ obterIdCNPq(cpf) ou obterIdCNPq(nomeCompleto, dataNascimento) """
        if len(args) == 1:
            return self.service.getIdentificadorCNPq(cpf=args[0],nomeCompleto='',dataNascimento='')
        elif len(args) == 2:
            return self.service.getIdentificadorCNPq(cpf='',nomeCompleto=args[0],dataNascimento=args[1])
        raise ValueError('obterIdCNPq deve receber 1 ou 2 parâmetros (cpf ou nomeCompleto e dataNascimento)')

    @Retry()
    def obterOcorrencia(self, idCNPq):
        return self.service.getOcorrenciaCV(id=idCNPq)
