from collections import deque
import heapq

def bfs(graph, start):
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
    nodes = graph.nodes()

    if not nodes:
        return True

    start = nodes[0]
    visited = bfs(graph, start)

    return len(visited) == len(nodes)

def reconstruct_path(predecessors, origem, destino):
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
    if not graph.has_node(origem):
        raise ValueError(f"Origem não encontrada no grafo: {origem}")

    nodes = graph.nodes()
    edges = graph.edges()

    distances = {node: float("inf") for node in nodes}
    predecessors = {node: None for node in nodes}

    distances[origem] = 0

    for _ in range(len(nodes) - 1):
        updated = False

        for u, v, attrs in edges:
            peso = attrs["peso"]

            if distances[u] != float("inf") and distances[u] + peso < distances[v]:
                distances[v] = distances[u] + peso
                predecessors[v] = u
                updated = True

            if not graph.directed:
                if distances[v] != float("inf") and distances[v] + peso < distances[u]:
                    distances[u] = distances[v] + peso
                    predecessors[u] = v
                    updated = True

        if not updated:
            break

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