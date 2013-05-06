import os
import json
import urllib
import urllib2
import cPickle
import codecs
import time
import datetime
import sys
reload(sys)
sys.setdefaultencoding("latin-1")
from xml2dict import XML2Dict
from unicodedata import normalize
from sets import Set
import pdb

class Ponto:
    def __init__(self,numero, dados):
        self.numero = numero

        self.latitude = u"%s"%str(dados[5])

        self.longitude = u"%s"%str(dados[4])
        self.ordem = 0

    def __repr__(self):
        return str(self.numero)

class Previsao:
    def __init__(self, xml):
        if not xml.previsao.has_key('ponto'):
            self.estimativas = []
            return None 
        if xml.previsao.ponto.has_key('estimativa'):
            self.estimativas = xml.previsao.ponto.estimativa
            if not isinstance(self.estimativas, list):
                self.estimativas = [self.estimativas,]
            self.estimativas.sort(key=lambda e: e.viagem.horario)
        else:
            self.estimativas = [] 

class PontoVitoria:
    pontos = []
    def __init__(self,url_base="http://rast.vitoria.es.gov.br/pontovitoria/"):
       self.url_base = url_base
       self.referer = "http://rast.vitoria.es.gov.br/pontovitoria/"
       self.key = None
    def get_key(self):
        """
        """
        if self.key:
            return self.key
        req = urllib2.Request("%sjs/principal/previsao.js"% self.url_base)        
        req.add_header('Referer',self.referer)
        pg = urllib2.urlopen(req)
        texto = pg.read()
        self.key= texto.split('key')[1].split('|')[2]
        return self.key

    def getPontos(self):
       """ 
       Retorna a lista de pontos do site ponto vitoria 
       Exemplo:

       >>> pv= PontoVitoria()
       >>> p = pv.getPontos()
       >>> len(p)
       998
       """

       if PontoVitoria.pontos:
           return PontoVitoria.pontos

       if not os.path.exists("dados/pontos/lista_de_pontos.json") :
            req = urllib2.Request("%sutilidades/retornaPontos" % self.url_base)        
            req.add_header('Referer',self.referer)
            pg = urllib2.urlopen(req)
            texto = pg.read()
            with open('dados/pontos/lista_de_pontos.json','w') as fp:
                fp.write(texto) 
        
       with open("dados/pontos/lista_de_pontos.json",'r') as fp:               
            pontos = json.loads(fp.read(),'utf-8')
      
       PontoVitoria.pontos = []
       for k in pontos.keys():
            k = k.strip()
            if k[0].isdigit():
                p=Ponto(int(k),pontos[k])
                PontoVitoria.pontos.append(p)
       return PontoVitoria.pontos

   
    
    def linhasQuePassamNoPonto(self,ponto): 
        """
        Esta Funcao detecta quais linhas de onibus passam no ponto informado como parametro.
        Exemplos de uso:
        
        >>> pv = PontoVitoria()
        >>> pv.linhasQuePassamNoPonto(6043) # ponto perto de minha casa
        [u'112', u'122', u'163', u'212', u'214', u'303']
        >>> pv.linhasQuePassamNoPonto(6166) # ponto perto da ufes
        [u'121', u'122', u'123', u'160', u'161', u'163', u'214', u'241']
        
        """
        linhas_file= "dados/pontos/%s.json" % ponto
        if not os.path.exists(linhas_file) :
            parametros = {'ponto_oid':ponto }
            req = urllib2.Request("%sutilidades/listaLinhaPassamNoPonto" % self.url_base,urllib.urlencode(parametros))        
            req.add_header('Referer',self.referer)
            pg = urllib2.urlopen(req)
            texto = pg.read()
            with open(linhas_file,'w') as fp:
                fp.write(texto)
        
        with open(linhas_file,'r') as fp:               
            linhas = json.loads(fp.read(),'utf-8')
        passam = []
        for k in linhas['data']:
             oid=k['linha'].split(" -")[0]
             passam.append(oid)
        return passam

    def linhasQueFazemPercurso(self, ponto_inicial, ponto_destino):
        """
        Retora a lista de linhas que fazem determinado percurso.
        Exemplos de uso:

        >>> pv = PontoVitoria()
        >>> pv.linhasQueFazemPercurso(6043,6166) # casa -> ufes
        [u'122', u'163', u'214']

        >>> pv.linhasQueFazemPercurso(6043,5059) # casa -> shopping vitoria/
        [u'212', u'214']

        """

        linhas_inicio = self.linhasQuePassamNoPonto(ponto_inicial)
        linhas_destino = self.linhasQuePassamNoPonto(ponto_destino)
        linhas_do_percurso = list(set(linhas_inicio).intersection(set(linhas_destino)))
        linhas_do_percurso.sort()
        return linhas_do_percurso
      
    def _getPrevisao(self,linha="163",ponto="6039"):
        url = "%sprevisao?ponto=%s&linha=%s&key=%s" % (self.url_base,ponto,linha,self.get_key())
        print url
        req = urllib2.Request(url)       
        req.add_header('Referer',self.referer)
        pg = urllib2.urlopen(req)
        return pg.read()

    def getPrevisao(self,linha="163",ponto="6039",cache = True):
        if cache: 
            prev_file= "dados/previsoes/%s/%s.json" % (linha,ponto)
            if not os.path.exists(prev_file):
                if not os.path.exists(os.path.dirname(prev_file)):
                    os.mkdir(os.path.dirname(prev_file))
                texto = self._getPrevisao(linha,ponto)
                with open(prev_file,'w') as fp:
                    fp.write(texto)
            else: 
                with open(prev_file,"r") as f:
                    texto = f.read()
        else:
            texto = self._getPrevisao(linha,ponto)
        xml = XML2Dict()
        r = xml.fromstring(texto)
        previsao = Previsao(r)
        return previsao
    
    def getPontosDaLinha(self,linha):
        """
        Retorna os pontos que pertecem a uma linha.
        Exemplos de uso:

        >>> pv = PontoVitoria()
        
        >>> pontos = pv.getPontosDaLinha('163')
        >>> len(pontos)
        89
        
        >>> pontos = pv.getPontosDaLinha('121')
        >>> len(pontos)
        141
        """
        pv = PontoVitoria()
        pontos = pv.getPontos()
        pontos_linha = []
        for p in pontos:
            linhas = pv.linhasQuePassamNoPonto(p.numero)
            if linha in linhas:
                pontos_linha.append(p)
        return pontos_linha


if __name__== "__main__":
    import doctest
    doctest.testmod()
    pv = PontoVitoria()
    p = pv.getPontosDaLinha(163)
    len(p)



