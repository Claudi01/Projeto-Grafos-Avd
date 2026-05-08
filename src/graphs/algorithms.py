from collections import deque


def bfs(graph, start):
    """
    Busca em largura - Breadth-First Search.

    Percorre o grafo em camadas, visitando primeiro os vizinhos
    mais próximos do nó inicial.

    Retorna a ordem de visita dos nós.
    """

    if not graph.has_node(start):
        raise ValueError(f"Nó inicial não encontrado no grafo: {start}")

    visited = set()
    order = []
    queue = deque()

    visited.add(start)
    queue.append(start)

    while queue:
        current = queue.popleft()
        order.append(current)

        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def bfs_layers(graph, start):
    """
    BFS por camadas.

    Retorna um dicionário indicando a distância em número de arestas
    entre o nó inicial e cada nó alcançado.

    Exemplo:
    {
        "REC": 0,
        "SSA": 1,
        "GRU": 1,
        "POA": 2
    }
    """

    if not graph.has_node(start):
        raise ValueError(f"Nó inicial não encontrado no grafo: {start}")

    visited = {start}
    layers = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                layers[neighbor] = layers[current] + 1
                queue.append(neighbor)

    return layers


def dfs(graph, start):
    """
    Busca em profundidade - Depth-First Search.

    Percorre o grafo avançando o máximo possível por um caminho
    antes de retornar e explorar outros vizinhos.

    Retorna a ordem de visita dos nós.
    """

    if not graph.has_node(start):
        raise ValueError(f"Nó inicial não encontrado no grafo: {start}")

    visited = set()
    order = []

    def visit(node):
        visited.add(node)
        order.append(node)

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visit(neighbor)

    visit(start)

    return order


def connected_components(graph):
    """
    Retorna as componentes conexas do grafo.

    Em um grafo conectado, haverá apenas uma componente contendo todos os nós.
    """

    visited = set()
    components = []

    for node in graph.nodes():
        if node not in visited:
            component = []

            def visit(current):
                visited.add(current)
                component.append(current)

                for neighbor in graph.neighbors(current):
                    if neighbor not in visited:
                        visit(neighbor)

            visit(node)
            components.append(component)

    return components


def is_connected(graph):
    """
    Verifica se o grafo é conectado.

    Um grafo é conectado quando todos os nós podem ser alcançados
    a partir de qualquer nó inicial.
    """

    nodes = graph.nodes()

    if not nodes:
        return True

    start = nodes[0]
    visited = bfs(graph, start)

    return len(visited) == len(nodes)