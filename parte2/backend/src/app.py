import json
import csv
from collections import defaultdict
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import time

from src.graphs.io import build_tmdb_graph 
from src.graphs.algorithms import bfs, dfs, dijkstra, bellman_ford_path  

app = Flask(__name__)
CORS(app)

grafo = build_tmdb_graph("data/tmdb_5000_credits_com_trailer.csv", threshold=2) 

@app.route('/api/grafo', methods=['GET'])
def get_grafo():
    nos_relevantes = sorted(grafo.nodes(), key=lambda n: grafo.degree(n), reverse=True)[:5000] 
    
    nodes = []
    for n in nos_relevantes:
        attrs = grafo.get_node_attrs(n)
        nodes.append({
            "id": n, 
            "label": attrs.get("title", n),
            "trailer": attrs.get("trailer", "") 
        })
        
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

@app.route('/api/dataset_insights', methods=['GET'])
def get_dataset_insights():
    caminho_csv = Path(__file__).resolve().parent.parent / "data" / "tmdb_5000_credits_com_trailer.csv" 
    
    ator_freq = defaultdict(int)
    distribuicao = []
    total_cast = 0
    total_crew = 0
    
    genero_cast = {0: 0, 1: 0, 2: 0}
    genero_crew = {0: 0, 1: 0, 2: 0}
    dept_freq = defaultdict(int)
    crew_freq = defaultdict(int)
    
    if not caminho_csv.exists():
        return jsonify({"details": "Dataset tmdb_5000_credits.csv não encontrado."}), 404
        
    try:
        with open(caminho_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("title", "Desconhecido")
                try:
                    cast_data = json.loads(row.get("cast", "[]"))
                    crew_data = json.loads(row.get("crew", "[]"))
                except:
                    cast_data = []
                    crew_data = []
                    
                cast_size = len(cast_data)
                crew_size = len(crew_data)
                
                total_cast += cast_size
                total_crew += crew_size
                
                if cast_size > 0 or crew_size > 0:
                    distribuicao.append({
                        "title": title,
                        "cast_size": cast_size,
                        "crew_size": crew_size
                    })
                    
                for ator in cast_data:
                    ator_freq[ator.get("name", "Desconhecido")] += 1
                    genero_cast[ator.get("gender", 0)] += 1
                    
                for membro in crew_data:
                    crew_freq[membro.get("name", "Desconhecido")] += 1
                    dept_freq[membro.get("department", "Desconhecido")] += 1
                    genero_crew[membro.get("gender", 0)] += 1
                    
        top_atores = sorted(ator_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_atores_formatado = [{"ator": k, "filmes": v} for k, v in top_atores]
        
        top_crew = sorted(crew_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_crew_formatado = [{"nome": k, "trabalhos": v} for k, v in top_crew]
        
        dept_formatado = [{"departamento": k, "total": v} for k, v in sorted(dept_freq.items(), key=lambda x: x[1], reverse=True)]
        
        genero_formatado = [
            {"categoria": "Elenco", "Feminino": genero_cast.get(1, 0), "Masculino": genero_cast.get(2, 0), "Não Informado": genero_cast.get(0, 0)},
            {"categoria": "Equipe Técnica", "Feminino": genero_crew.get(1, 0), "Masculino": genero_crew.get(2, 0), "Não Informado": genero_crew.get(0, 0)}
        ]
        
        distribuicao.sort(key=lambda x: x["cast_size"] + x["crew_size"], reverse=True)
        distribuicao_amostra = distribuicao[:100]
        
        proporcao = [
            {"name": "Elenco (Cast)", "value": total_cast},
            {"name": "Equipe Técnica (Crew)", "value": total_crew}
        ]
        
        return jsonify({
            "top_atores": top_atores_formatado,
            "distribuicao": distribuicao_amostra,
            "proporcao": proporcao,
            "top_crew": top_crew_formatado,
            "departamentos": dept_formatado,
            "genero": genero_formatado
        })
    except Exception as e:
        return jsonify({"details": f"Erro ao processar insights: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)