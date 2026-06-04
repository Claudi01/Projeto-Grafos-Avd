import { useState } from 'react';

interface Metricas {
  ordem: number;
  tamanho: number;
  densidade: number;
}

interface Resultado {
  caminho: string[];
  custo: number;
  tempo_ms: number;
}

interface PainelMetricasProps {
  metricas: Metricas;
  nosDisponiveis: any[];
  onBuscar: (origem: string, destino: string, algoritmo: string) => void;
  resultado: Resultado;
}

export default function PainelMetricas({ metricas, nosDisponiveis, onBuscar, resultado }: PainelMetricasProps) {
  const [origem, setOrigem] = useState('');
  const [destino, setDestino] = useState('');
  const [algoritmo, setAlgoritmo] = useState('bfs');

  return (
    <div className="w-80 bg-darkcard p-4 flex flex-col gap-4 border-l border-gray-800 h-full overflow-y-auto">
      <h2 className="text-xl font-bold text-imdb">Métricas Globais</h2>
      
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-black p-3 rounded border border-gray-800">
          <p className="text-gray-400 text-xs">Ordem</p>
          <p className="text-lg font-semibold">{metricas.ordem}</p>
        </div>
        <div className="bg-black p-3 rounded border border-gray-800">
          <p className="text-gray-400 text-xs">Arestas</p>
          <p className="text-lg font-semibold">{metricas.tamanho}</p>
        </div>
      </div>

      <hr className="border-gray-800 my-2" />

      <h2 className="text-xl font-bold text-imdb">Buscar Rota</h2>
      
      <select 
        className="bg-black border border-gray-700 rounded p-2 text-sm w-full"
        value={origem} onChange={e => setOrigem(e.target.value)}
      >
        <option value="">Selecione a Origem...</option>
        {nosDisponiveis.map(n => <option key={`orig-${n.id}`} value={n.id}>{n.label}</option>)}
      </select>

      <select 
        className="bg-black border border-gray-700 rounded p-2 text-sm w-full"
        value={destino} onChange={e => setDestino(e.target.value)}
      >
        <option value="">Selecione o Destino...</option>
        {nosDisponiveis.map(n => <option key={`dest-${n.id}`} value={n.id}>{n.label}</option>)}
      </select>

      <select 
        className="bg-black border border-gray-700 rounded p-2 text-sm w-full"
        value={algoritmo} onChange={e => setAlgoritmo(e.target.value)}
      >
        <option value="bfs">Busca em Largura (BFS)</option>
        <option value="dfs">Busca em Profundidade (DFS)</option>
        <option value="dijkstra">Dijkstra</option>
        <option value="bellman-ford">Bellman-Ford</option>
      </select>

      <button 
        onClick={() => onBuscar(origem, destino, algoritmo)}
        className="bg-imdb text-black font-bold py-2 rounded hover:bg-yellow-500 transition-colors"
        disabled={!origem || !destino}
      >
        Calcular Rota
      </button>

      {resultado.tempo_ms > 0 && (
        <div className="mt-4 flex flex-col gap-2">
          <div className="bg-black p-3 rounded border border-gray-800 border-l-4 border-l-imdb">
            <p className="text-gray-400 text-xs">Tempo de Execução</p>
            <p className="text-lg font-semibold">{resultado.tempo_ms} ms</p>
          </div>
          <div className="bg-black p-3 rounded border border-gray-800">
            <p className="text-gray-400 text-xs">Custo da Rota</p>
            <p className="text-lg font-semibold">{resultado.custo}</p>
          </div>
          <div className="bg-black p-3 rounded border border-gray-800">
            <p className="text-gray-400 text-xs">Nós Percorridos</p>
            <p className="text-lg font-semibold">{resultado.caminho.length}</p>
          </div>
        </div>
      )}
    </div>
  );
}