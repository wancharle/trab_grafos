#! -*- coding: utf-8 -*-
import os
import json
from libs.pontovitoria import PontoVitoria, Ponto
import grafo
from grafo import Caminho, Vertice

class Linha():
    """
    Classe resposavel por gerar e manipular o grafo/caminho percorrido por uma linha de onibus.

    >>> l = Linha('161')
    >>> l.save_json()
    >>> len(l.grafo.vertices)
    133
    """
    def __init__(self,linha_id):
        self.grafo = Caminho()
        self.linha_id = linha_id
        # tenta carregar pontos ordenados do cache ou gera novo cache
        pontos_ordenados = self.load_json() 
        if not pontos_ordenados:
           pontos_ordenados = self.gerar_pontos_ordenados()

        # gerando o grafo da linha 
        v_anterior = None
        ordem = 0
        for p in pontos_ordenados:
            ordem+=1
            if not p.ordem:
                p.ordem = ordem
            v = Vertice(p.numero,p)
            self.grafo.add(v)
            if v_anterior:
                self.grafo.add_arco(v_anterior,v)
            v_anterior = v

    def gerar_pontos_ordenados(self):
        pontos_ordenados = []
        pv = PontoVitoria()
        pontos = pv.getPontosDaLinha(self.linha_id)
        
        # obtendo estimativas de horarios por ponto
        viagens = {}
        estimativas = {}
        for p in pontos:
            previsao = pv.getPrevisao(self.linha_id,p.numero)
            estimativas[p.numero]=previsao.estimativas
            p.viagens= {}
            for e in previsao.estimativas:
                viagem_id = e.viagem.oid
                p.viagens[viagem_id]=e
                if viagens.has_key(viagem_id):
                    if p not in viagens[viagem_id]:
                        viagens[viagem_id].append(p) 
                else: 
                    viagens[viagem_id]=[p]
     
        # obtendo viagem presente em todos os pontos
        vi_sorted = sorted([ (len(value),key) for (key,value) in viagens.items()])
        if len(vi_sorted):
            viagem_id=vi_sorted[-1][1]
            viagens[viagem_id].sort(key=lambda p: p.viagens[viagem_id].horarioEstimado) 
            pontos_ordenados = viagens[viagem_id]
        return pontos_ordenados

    def load_json(self):
        pontos_ordenados = []
        linha_file = "dados/linhas_ordenada/%s.json" % self.linha_id
        if os.path.exists(linha_file):
            with open(linha_file,'r') as fp:               
                pontos = json.loads(fp.read(),'utf-8')
            for p in pontos:
                p[4] = p['longitude']
                p[5] = p['latitude']
                ponto = Ponto( p['ponto'],p)
                ponto.ordem = p['ordem']
                pontos_ordenados.append(ponto)
        return pontos_ordenados

    def __repr__(self):
        """ imprime a classe no terminal """
        text = u"%s\n" % self.linha_id  
        vertice = self.grafo.get_first()
        while vertice:
            text += "%s --> " % vertice.data.numero
            vertice = self.grafo.get_sucessor(vertice)
        return text[:-4]

    def save_json(self):
        l = self.linha_id
        linha_file= "dados/linhas_ordenada/%s.json" % l
        #if not os.path.exists(linha_file) :
        with open(linha_file,'w') as fp:
            fp.write("[")
            saida = ""
            ordem = 0
            vertice = self.grafo.get_first()
            while vertice:
                ordem+=1
                ponto = vertice.data 
                s = "{"
                s += "\"linha\": \"%s\",\"ponto\": %s,\"ordem\": %s," % (l,ponto.numero, ordem)
                s += "\"latitude\":\"%s\",\"longitude\":\"%s\"}," % (ponto.latitude, ponto.longitude)
                saida +=s
                vertice = self.grafo.get_sucessor(vertice)
            saida = saida[:-1]
            fp.write(saida+"]")

    def pontos_de_intersecao_com(self, outra_linha):
        pontos = []
        for v in self.grafo.vertices:
            for v2 in outra_linha.grafo.vertices:
                if v.data.numero == v2.data.numero and v.data.numero not in pontos: 
                    pontos.append(v.data.numero)
                    break

        return pontos

    def get_ordem_do_ponto(self,ponto_numero):
        vertice = self.grafo.get_vertice(ponto_numero)
        return vertice.data.ordem

if __name__== "__main__":
    l = Linha('163')
    l.save_json()
    #l = Linha('211')
    #l.save_json()
    #l = Linha('122')
    #l.save_json()
    import doctest
    doctest.testmod()
    
   
