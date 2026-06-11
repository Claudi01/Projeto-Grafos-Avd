import json
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import time

from src.graphs.io import build_tmdb_graph 
from src.graphs.algorithms import bfs, dfs, dijkstra, bellman_ford_path  

app = Flask(__name__)
CORS(app)

grafo = build_tmdb_graph("data/tmdb_5000_credits.csv", threshold=2)

@app.route('/api/grafo', methods=['GET'])
def get_grafo():
    # carregar todos os nós
    nos_relevantes = sorted(grafo.nodes(), key=lambda n: grafo.degree(n), reverse=True)[:5000] 
    
    nodes = [{"id": n, "label": grafo.get_node_attrs(n).get("title", n)} for n in nos_relevantes]
    edges = []
    
    for u, v, attrs in grafo.edges():
        if u in nos_relevantes and v in nos_relevantes:
            edges.append({"source": u, "target": v, "weight": attrs.get("peso", 1)})

    return jsonify({"nodes": nodes, "links": edges})

@app.route('/api/metricas', methods=['GET'])
def get_metricas():
    return jsonify({
        "ordem": grafo.order(),
        "tamanho": grafo.size(),
        "densidade": grafo.density()
    })

@app.route('/api/caminho', methods=['POST'])
def calcular_caminho():
    data = request.json
    origem = str(data.get('origem'))
    destino = str(data.get('destino'))
    algoritmo = data.get('algoritmo', '').lower()

    if not grafo.has_node(origem) or not grafo.has_node(destino):
        return jsonify({"error": "Origem ou destino não encontrados no grafo"}), 404

    inicio = time.time()
    caminho, custo = [], 0

    if algoritmo == "bfs":
        caminho = bfs(grafo, origem)  
    elif algoritmo == "dfs":
        caminho = dfs(grafo, origem)  
    elif algoritmo == "dijkstra":
        resultado = dijkstra(grafo, origem, destino)  
        caminho, custo = resultado["caminho"], resultado["custo"]
    elif algoritmo == "bellman-ford":
        resultado = bellman_ford_path(grafo, origem, destino)  
        caminho, custo = resultado["caminho"], resultado["custo"]
    else:
        return jsonify({"error": "Algoritmo não suportado"}), 400

    tempo_ms = (time.time() - inicio) * 1000

    return jsonify({
        "caminho": caminho,
        "custo": custo,
        "tempo_ms": round(tempo_ms, 2)
    })

@app.route('/api/report', methods=['GET'])
def get_report():
    OUT_DIR = Path(__file__).resolve().parent.parent / "out"
    caminho_report = OUT_DIR / "parte2_report.json"
    
    if not caminho_report.exists():
        return jsonify({
            "details": f"Arquivo parte2_report.json não encontrado em {caminho_report}. Execute 'py -m src.solve' no terminal do backend para gerá-lo."
        }), 404
        
    try:
        with open(caminho_report, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            "details": f"Erro interno ao ler o arquivo JSON: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)