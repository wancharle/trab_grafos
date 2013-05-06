#! -*- coding: utf-8 -*-
from libs.pontovitoria import PontoVitoria
from linhas import Linha

class RotaIndireta():
    def __init__(self, p1,p2, l1,l2, pontos_intersecao):
        self.l1 = l1
        self.l2 = l2
        self.p1 = p1
        self.p2 = p2
        self.pontos_intersecao = pontos_intersecao
        self.pontos_de_parada = []
    def get_pontos_de_parada(self):
        """ 
        Para diferenciar entre os pontos de ida e volta é preciso escolher 
        apenas os pontos com ordem menor que a do ponto de destino na linha destino.
        
        """
        if len(self.pontos_de_parada):
            return self.pontos_de_parada
        pontos_de_parada = []
        ordem_destino = self.l2.get_ordem_do_ponto(self.p2)
        for p in self.pontos_intersecao:
            if self.l2.get_ordem_do_ponto(p) < ordem_destino:
                pontos_de_parada.append(p)
        self.pontos_de_parada = pontos_de_parada
        return pontos_de_parada
    
    def to_json(self):
        """
        converte esta rota na sua represetação em formato json
        """
        pontosjson = ""
        for p in self.get_pontos_de_parada():
            pontosjson +="\"%s\", " % p
        pontosjson = pontosjson[:-2] # remove ultima virgula   
        return "{ \"linha1\":\"%s\", \"linha2\":\"%s\", \"pontos_de_parada\": [%s] }" % (self.l1.linha_id, self.l2.linha_id, pontosjson)

    def __repr__(self):
        return u"%s --> %s\t  (%d, %d, %d, %d)" % (self.l1.linha_id,self.l2.linha_id, len(self.l1.grafo.vertices), len(self.l2.grafo.vertices),len(self.pontos_intersecao),len(self.get_pontos_de_parada()))

class Rotas:
    """ 
    Essa classe descobre quais são as linhas diretas e indiretas que fazem determinado percurso

    >>> e = Rotas(6151,5059)
    >>> e.linhas_diretas
    []
    >>> len(e.linhas_indiretas)
    26
    >>> e.save_json()
    """

    def __init__(self, p_inicio, p_destino):
        self.p1 = p_inicio
        self.p2 = p_destino
        pv = PontoVitoria()
        linhas_diretas = pv.linhasQueFazemPercurso(p_inicio, p_destino)
        outras_linhas = set(pv.linhasQuePassamNoPonto(p_inicio)) - set(linhas_diretas)
        linhas_destino = set(pv.linhasQuePassamNoPonto(p_destino)) - set(linhas_diretas)

        linhas_indiretas = []
        for l in outras_linhas:
            l1 = Linha(l)
            for ld in linhas_destino:
                l2 = Linha(ld)
                pontos_de_intersecao = l1.pontos_de_intersecao_com(l2) 
                if pontos_de_intersecao:
                    linhas_indiretas.append( RotaIndireta(p_inicio,p_destino,l1,l2,pontos_de_intersecao))
                   
        
        self.linhas_diretas = linhas_diretas

        self.linhas_indiretas = []
        for r in linhas_indiretas:
            if len(r.get_pontos_de_parada())>0:
                self.linhas_indiretas.append(r)
        linhas_indiretas

    def save_json(self):
        """
        salva as rotas descobertas num arquivo de nome  PONTOINICIO_PONTODESTINO.json
        """
        rotas_diretas = ""
        for r in self.linhas_diretas:
            rotas_diretas +="\"%s\", " % r
        rotas_diretas= rotas_diretas[:-2]

        rotas_indiretas = ""
        for r in self.linhas_indiretas:
            rotas_indiretas +="%s, " % r.to_json()
        rotas_indiretas = rotas_indiretas[:-2]

        texto_json = "{ \"ponto_inicial\":\"%s\", \"ponto_destino\":\"%s\",\n\"linhas_diretas\":[%s],\n\"linhas_indiretas\":[%s] }" % (self.p1,self.p2, rotas_diretas, rotas_indiretas)
        with open("dados/rotas/%s_%s.json" % (self.p1,self.p2),'w') as f:
            f.write(texto_json)

    def __repr__(self):
        texto = "ROTA:  %s\t->\t%s\n" % (self.p1, self.p2)
        texto+= "Linhas diretas: %s\n" % self.linhas_diretas
        texto+= "linhas indiretas:\nLinha 1 --> Linha2\t (n_pontos1, n_pontos2, n_pontos_intersecao,n_pontos_parada)\n"
        for l in self.linhas_indiretas:
            texto+=str(l)+"\n"
        return texto



def test():
    pontos= [
    ['6043','Maria Ortiz' ],
    ['5059', 'Shopping Vitoria'],
    ['5029', 'Shopping Bullevard'],
    ['6166', 'UFES'],
    ['4033', 'UFES - campus Maruipe'],
    ['7041', 'São Pedro'],
    ['2137', 'Rodoviária de Vitoria'],
    ['6163', 'Aeroporto']
    ]

    for p in pontos:
        for p2 in pontos:
            if p != p2:
                r=Rotas(p[0],p2[0])
                print "rota: %s --> %s calculada" %(p[0],p2[0])
                r.save_json()

if __name__== "__main__":
    test()
