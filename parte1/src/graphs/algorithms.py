from collections import deque
import heapq

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

def reconstruct_path(predecessors, origem, destino):
    """
    Reconstrói o caminho mínimo a partir do dicionário de predecessores.

    Exemplo:
    predecessors = {
        "POA": "GRU",
        "GRU": "REC"
    }

    origem = "REC"
    destino = "POA"

    Retorno:
    ["REC", "GRU", "POA"]
    """

    path = []
    current = destino

    while current is not None:
        path.append(current)

        if current == origem:
            break

        current = predecessors.get(current)

    path.reverse()

    if not path or path[0] != origem:
        return []

    return path


def dijkstra(graph, origem, destino):
    """
    Algoritmo de Dijkstra.

    Calcula o caminho de menor custo entre origem e destino
    em um grafo com pesos não negativos.

    Retorna:
    {
        "origem": "REC",
        "destino": "POA",
        "custo": 4.0,
        "caminho": ["REC", "GRU", "POA"]
    }
    """

    if not graph.has_node(origem):
        raise ValueError(f"Origem não encontrada no grafo: {origem}")

    if not graph.has_node(destino):
        raise ValueError(f"Destino não encontrado no grafo: {destino}")

    distances = {node: float("inf") for node in graph.nodes()}
    predecessors = {node: None for node in graph.nodes()}

    distances[origem] = 0

    priority_queue = [(0, origem)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        if current_node == destino:
            break

        for neighbor, attrs in graph.neighbors_with_attrs(current_node):
            peso = attrs["peso"]

            if peso < 0:
                raise ValueError("Dijkstra não aceita pesos negativos.")

            new_distance = current_distance + peso

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))

    caminho = reconstruct_path(predecessors, origem, destino)

    return {
        "origem": origem,
        "destino": destino,
        "custo": distances[destino],
        "caminho": caminho
    }


def bellman_ford(graph, origem):
    """
    Algoritmo de Bellman-Ford.

    Calcula as menores distâncias a partir de uma origem.
    Diferentemente do Dijkstra, aceita pesos negativos.

    Também detecta ciclos negativos.

    Retorna:
    {
        "distancias": {...},
        "predecessores": {...}
    }
    """

    if not graph.has_node(origem):
        raise ValueError(f"Origem não encontrada no grafo: {origem}")

    nodes = graph.nodes()
    edges = graph.edges()

    distances = {node: float("inf") for node in nodes}
    predecessors = {node: None for node in nodes}

    distances[origem] = 0

    # Relaxamento das arestas |V| - 1 vezes
    for _ in range(len(nodes) - 1):
        updated = False

        for u, v, attrs in edges:
            peso = attrs["peso"]

            if distances[u] != float("inf") and distances[u] + peso < distances[v]:
                distances[v] = distances[u] + peso
                predecessors[v] = u
                updated = True

            # Se o grafo for não direcionado, é necessário relaxar o sentido inverso.
            # Em graph.edges(), a aresta aparece uma única vez.
            if not graph.directed:
                if distances[v] != float("inf") and distances[v] + peso < distances[u]:
                    distances[u] = distances[v] + peso
                    predecessors[u] = v
                    updated = True

        if not updated:
            break

    # Verificação de ciclo negativo
    for u, v, attrs in edges:
        peso = attrs["peso"]

        if distances[u] != float("inf") and distances[u] + peso < distances[v]:
            raise ValueError("Ciclo negativo detectado no grafo.")

        if not graph.directed:
            if distances[v] != float("inf") and distances[v] + peso < distances[u]:
                raise ValueError("Ciclo negativo detectado no grafo.")

    return {
        "distancias": distances,
        "predecessores": predecessors
    }


def bellman_ford_path(graph, origem, destino):
    """
    Calcula o caminho mínimo entre origem e destino usando Bellman-Ford.
    """

    resultado = bellman_ford(graph, origem)

    distancias = resultado["distancias"]
    predecessores = resultado["predecessores"]

    caminho = reconstruct_path(predecessores, origem, destino)

    return {
        "origem": origem,
        "destino": destino,
        "custo": distancias[destino],
        "caminho": caminho
    }