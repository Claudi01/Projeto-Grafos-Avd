class Graph:
    def __init__(self, directed=False, allow_negative_weights=False):
        self.directed = directed
        self.allow_negative_weights = allow_negative_weights
        self._adj = {}
        self._node_attrs = {}

    def add_node(self, node, **attrs):
        if node not in self._adj:
            self._adj[node] = {}

        if node not in self._node_attrs:
            self._node_attrs[node] = {}

        self._node_attrs[node].update(attrs)

    def add_edge(self, origem, destino, peso=1.0, **attrs):
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
        return list(self._adj.keys())

    def edges(self):
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
        if node not in self._adj:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return list(self._adj[node].keys())

    def neighbors_with_attrs(self, node):
        if node not in self._adj:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return list(self._adj[node].items())

    def get_edge_attrs(self, origem, destino):
        if origem not in self._adj or destino not in self._adj[origem]:
            raise ValueError(f"Aresta não encontrada: {origem} -> {destino}")

        return self._adj[origem][destino]

    def get_node_attrs(self, node):
        if node not in self._node_attrs:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return self._node_attrs[node]

    def degree(self, node):
        if node not in self._adj:
            raise ValueError(f"Nó não encontrado no grafo: {node}")

        return len(self._adj[node])

    def order(self):
        return len(self._adj)

    def size(self):
        return len(self.edges())

    def density(self):
        v = self.order()
        e = self.size()

        if v < 2:
            return 0

        if self.directed:
            return e / (v * (v - 1))

        return (2 * e) / (v * (v - 1))

    def has_node(self, node):
        return node in self._adj

    def has_edge(self, origem, destino):
        return origem in self._adj and destino in self._adj[origem]