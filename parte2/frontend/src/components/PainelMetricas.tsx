import { useState, useMemo, useEffect, useRef } from 'react';

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
  origem: string;
  setOrigem: (val: string) => void;
  destino: string;
  setDestino: (val: string) => void;
}

const SearchableSelect = ({ options, value, onChange, placeholder }: { options: any[], value: string, onChange: (val: string) => void, placeholder: string }) => {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const sortedOptions = useMemo(() => {
    return [...options].sort((a, b) => (a.label || '').localeCompare(b.label || ''));
  }, [options]);

  const filteredOptions = useMemo(() => {
    if (!search) return sortedOptions;
    return sortedOptions.filter(opt => 
      (opt.label || '').toLowerCase().includes(search.toLowerCase())
    );
  }, [sortedOptions, search]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        const selectedOpt = options.find(o => String(o.id) === String(value));
        if (selectedOpt) setSearch(selectedOpt.label);
        else setSearch('');
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef, value, options]);

  useEffect(() => {
    const selectedOpt = options.find(o => String(o.id) === String(value));
    if (selectedOpt) setSearch(selectedOpt.label);
  }, [value, options]);

  return (
    <div ref={wrapperRef} className="relative w-full">
      <input
        type="text"
        className="w-full bg-black border border-gray-700 rounded p-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-imdb"
        placeholder={placeholder}
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setIsOpen(true);
          onChange(''); 
        }}
        onFocus={() => setIsOpen(true)}
      />
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-black border border-gray-700 rounded shadow-lg max-h-60 overflow-y-auto">
          {filteredOptions.length > 0 ? (
            filteredOptions.map((opt) => (
              <div
                key={opt.id}
                className="p-2 text-sm text-gray-200 hover:bg-gray-800 hover:text-white cursor-pointer"
                onClick={() => {
                  onChange(String(opt.id));
                  setSearch(opt.label);
                  setIsOpen(false);
                }}
              >
                {opt.label}
              </div>
            ))
          ) : (
            <div className="p-2 text-sm text-gray-500">Nenhum filme encontrado.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default function PainelMetricas({ 
  metricas, 
  nosDisponiveis, 
  onBuscar, 
  resultado,
  origem,
  setOrigem,
  destino,
  setDestino
}: PainelMetricasProps) {
  const [algoritmo, setAlgoritmo] = useState('bfs');

  return (
    <div className="w-80 bg-darkcard p-4 flex flex-col gap-4 border-l border-gray-800 h-full overflow-y-auto z-20">
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
      
      <SearchableSelect 
        options={nosDisponiveis} 
        value={origem} 
        onChange={setOrigem} 
        placeholder="Digite a Origem..." 
      />

      <SearchableSelect 
        options={nosDisponiveis} 
        value={destino} 
        onChange={setDestino} 
        placeholder="Digite o Destino..." 
      />

      <select 
        className="bg-black border border-gray-700 rounded p-2 text-sm w-full text-white"
        value={algoritmo} onChange={e => setAlgoritmo(e.target.value)}
      >
        <option value="bfs">Busca em Largura (BFS)</option>
        <option value="dfs">Busca em Profundidade (DFS)</option>
        <option value="dijkstra">Dijkstra</option>
        <option value="bellman-ford">Bellman-Ford</option>
      </select>

      <button 
        onClick={() => onBuscar(origem, destino, algoritmo)}
        className="bg-imdb text-black font-bold py-2 rounded hover:bg-yellow-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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