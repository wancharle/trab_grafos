#!/usr/bin/python
#! -*- coding: utf-8 -*-
from linhas import Linha
from rotas import Rotas

# corigindo acentos
import sys
reload(sys)
sys.setdefaultencoding("latin-1")

def testes():
    """ testando modulos desenvolvidos """
    import libs.pontovitoria
    import grafo
    import linhas
    import rotas
    import doctest
    doctest.testmod(pontovitoria)
    doctest.testmod(grafo)
    doctest.testmod(linhas)
    doctest.testmod(rotas)
 
def comandos():
    if len(sys.argv) > 1 :
        comando = sys.argv[1]
        if comando == "testes":
            testes()
        
        elif comando == "linha":
            if len(sys.argv) > 2:
                linha_id = sys.argv[2]
                l = Linha(linha_id)
                l.save_json()
                print l
            else:
                print "Sintaxe errada no comando. Sintaxe correta: linha <ponto>"
                print "exemplo: linha 161"
        elif comando == "rotas":
            if len(sys.argv) > 3: 
                p1 = sys.argv[2]
                p2 = sys.argv[3]
                rota = Rotas(p1,p2)
                rota.save_json()
                print rota
            else:
                print "Sintaxe errada no comando. Sintaxe correta: rotas <ponto_inicio> <ponto_destino>"
                print "exemplo: rotas 6151 5059"
                
        else:
            print "este comando não existe"
    else:
        print "\nComo usar este programa: \n$ python trab_grafos.py <comando> <parametros>"
        print "\nComandos:"
        print "linha \tgera o grafo de caminho da linha de onibus"
        print "rotas \tlistas as rotas dispontiveis entre dois pontos"

if __name__ == "__main__":
    comandos()
