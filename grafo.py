
class Vertice:
    """ implementacao usando lista de adjacencias para grafos direcionados """

    def __init__(self, name,data):
        self.name = str(name)
        self.data = data
        self.in_neighborhood = set()
        self.out_neighborhood = set()
        self.grau_de_saida = 0
        self.grau_de_entrada = 0

    def __hash__(self):
        return hash(self.name)

    def __lt__(self,outro):
        """ funcao de comparacao de vertice para usar em metodos de ordenacao """
        return self.name < self.name

    def __eq__(self,outro):
        """ funcao de comparacao de vertice para usar em metodos de ordenacao """
        return self.data.numero == self.data.numero 
  
    def __repr__(self):
        return u"%s" % self.name

    def add_arco(self,v_origem, v_destino):
        if v_origem.name == self.name:
            self.out_neighborhood.add(v_destino)
            self.grau_de_saida = len(self.out_neighborhood)
        if v_destino.name == self.name:
            self.in_neighborhood.add(v_origem)
            self.grau_de_entrada = len(self.in_neighborhood)

    def remove_arco(self,v_origem,v_destino):
        if v_origem.name == self.name:
            self.out_neighborhood.remove(v_destino)
            self.grau_de_saida = len(self.out_neighborhood)
        if v_destino.name == self.name:
            self.in_neighborhood.remove(v_origem)
            self.grau_de_entrada = len(self.in_neighborhood)
   
class Grafo:
    def __init__(self):
        self.vertices_hash = {}
        self.vertices = []
        self.arcos = []

    def add(self,vertice):
        if self.vertices_hash.has_key(str(vertice.name)):
            self.remove(self.vertices_hash[str(vertice.name)])
        self.vertices_hash[str(vertice.name)]=vertice
        self.vertices.append(vertice)

    def remove(self,vertice):
        self.vertices_hash[str(vertice.name)] = None
        self.vertices.remove(vertice)

    def get_vertice(self,name):
        return self.vertices_hash[str(name)] 

    def add_arco(self,v_origem,v_destino):
        v_origem.add_arco(v_origem, v_destino)
        v_destino.add_arco(v_origem, v_destino)
        self.arcos.append( (v_origem, v_destino) )

    def remove_arco(self,v_origem,v_destino):
        v_origem.remove_arco(v_origem, v_destino)
        v_destino.remove_arco(v_origem, v_destino)
        self.arcos.remove( (v_origem, v_destino) )

    def get_neighbours(self,vertice):
        return vertice.in_neighborhood | vertice.out_neighborhood
       
    
class Caminho(Grafo):
    def __init__(self):
        Grafo.__init__(self)
        self.first_vertice = None
        self.last_vertice = None

    def get_first(self):
        """ Retorna o primeiro vertice do caminho """
        for v in self.vertices:
            if v.grau_de_entrada == 0 :
                return v
        return None

    def get_last(self):
        """ Retorna o ultimo vertice do caminho """
        for v in self.vertices:
            if v.grau_de_saida == 0:
                return v
        return None

    def get_predecessor(self, vertice):
        for i in iter(vertice.in_neighborhood):
            return i
        return None   

    def get_sucessor(self, vertice):
        for i in iter(vertice.out_neighborhood):
            return i
        return None
