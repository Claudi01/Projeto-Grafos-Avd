class Graph:
    """
    Estrutura de grafo baseada em lista de adjacência.

    Cada nó representa um aeroporto.
    Cada aresta representa uma conexão entre aeroportos.

    O grafo da Parte 1 é não direcionado. Portanto, ao adicionar
    uma aresta REC -> SSA, também será criada a ligação SSA -> REC.
    """

    def __init__(self, directed=False, allow_negative_weights=False):
        self.directed = directed
        self.allow_negative_weights = allow_negative_weights
        self._adj = {}
        self._node_attrs = {}

    def add_node(self, node, **attrs):
        """
        Adiciona um nó ao grafo.

        Exemplo:
        graph.add_node("REC", cidade="Recife", regiao="Nordeste")
        """

        if node not in self._adj:
            self._adj[node] = {}

        if node not in self._node_attrs:
            self._node_attrs[node] = {}

        self._node_attrs[node].update(attrs)

    def add_edge(self, origem, destino, peso=1.0, **attrs):
        """
        Adiciona uma aresta ao grafo.

        Em grafo não direcionado, a aresta é espelhada automaticamente.
        Exemplo:
        REC -> SSA
        SSA -> REC
        """

        if origem == destino:
            raise ValueError(f"Aresta inválida: origem e destino iguais ({origem}).")

        if peso < 0 and not self.allow_negative_weights:
            raise ValueError(
                "Pesos negativos não são permitidos neste grafo. "
            )

        if origem not in self._adj:
            self.add_node(origem)

        if destino not in self._adj:
            self.add_node(destino)

        edge_attrs = {
            "peso": float(peso),
            **attrs
        }

        self._adj[origem][destino] = edge_attrs

        if not self.directed:
            self._adj[destino][origem] = edge_attrs.copy()

    def nodes(self):
        """
        Retorna a lista de nós do grafo.
        """

        return list(self._adj.keys())

    def edges(self):
        """
        Retorna a lista de arestas do grafo.

        Em grafo não direcionado, evita contar a mesma aresta duas vezes.
        """

        arestas = []
        visitadas = set()

        for origem in self._adj:
            for destino, attrs in self._adj[origem].items():

                if self.directed:
                    chave = (origem, destino)
                else:
                    chave = tuple(sorted([origem, destino]))

                if chave not in visitadas:
                    visitadas.add(chave)
                    arestas.append((origem, destino, attrs))

        return arestas

    def neighbors(self, node):
        """
        Retorna os vizinhos de um nó.
        """

        if node not in self._adj:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return list(self._adj[node].keys())

    def neighbors_with_attrs(self, node):
        """
        Retorna os vizinhos com os atributos da aresta.

        Exemplo de retorno:
        [
            ("SSA", {"peso": 1.0, "tipo_conexao": "regional"}),
            ("GRU", {"peso": 2.0, "tipo_conexao": "hub"})
        ]
        """

        if node not in self._adj:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return list(self._adj[node].items())

    def get_edge_attrs(self, origem, destino):
        """
        Retorna os atributos de uma aresta específica.
        """

        if origem not in self._adj or destino not in self._adj[origem]:
            raise ValueError(f"Aresta não encontrada: {origem} -> {destino}")

        return self._adj[origem][destino]

    def get_node_attrs(self, node):
        """
        Retorna os atributos de um nó.
        """

        if node not in self._node_attrs:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return self._node_attrs[node]

    def degree(self, node):
        """
        Retorna o grau de um nó.

        Grau = quantidade de conexões do aeroporto.
        """

        if node not in self._adj:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return len(self._adj[node])

    def order(self):
        """
        Ordem do grafo = quantidade de nós.
        """

        return len(self._adj)

    def size(self):
        """
        Tamanho do grafo = quantidade de arestas.

        Em grafo não direcionado, cada aresta é contada apenas uma vez.
        """

        return len(self.edges())

    def density(self):
        """
        Densidade do grafo não direcionado:

        densidade = 2E / V(V - 1)
        """

        v = self.order()
        e = self.size()

        if v < 2:
            return 0

        if self.directed:
            return e / (v * (v - 1))

        return (2 * e) / (v * (v - 1))

    def has_node(self, node):
        """
        Verifica se um nó existe no grafo.
        """

        return node in self._adj

    def has_edge(self, origem, destino):
        """
        Verifica se existe aresta entre origem e destino.
        """

        return origem in self._adj and destino in self._adj[origem]