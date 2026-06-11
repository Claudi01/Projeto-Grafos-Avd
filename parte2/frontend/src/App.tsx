import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import GrafoInterativo from './components/GrafoInterativo';
import PainelMetricas from './components/PainelMetricas';
import AVDDashboard from './components/AVDDashboard';

interface Metricas {
  ordem: number;
  tamanho: number;
  densidade: number;
}

interface Node {
  id: string | number;
  label?: string;
  [key: string]: any;
}

interface LinkType {
  source: string | number | any;
  target: string | number | any;
  weight?: number;
  [key: string]: any;
}

interface DadosGrafo {
  nodes: Node[];
  links: LinkType[];
}

interface ResultadoCaminho {
  caminho: string[];
  custo: number;
  tempo_ms: number;
}

function Home() {
  return (
    <div className="flex flex-col items-center justify-center w-full h-full gap-6">
      <h1 className="text-5xl font-bold text-center">Explorador de Grafos</h1>
      <Link to="/grafo" className="px-6 py-3 bg-imdb text-black font-bold rounded text-lg hover:bg-yellow-500 transition">
        Aceder ao Grafo
      </Link>
    </div>
  );
}

export default function App() {
  const [metricas, setMetricas] = useState<Metricas>({ ordem: 0, tamanho: 0, densidade: 0 });
  const [dadosGrafo, setDadosGrafo] = useState<DadosGrafo>({ nodes: [], links: [] });
  const [resultado, setResultado] = useState<ResultadoCaminho>({ caminho: [], custo: 0, tempo_ms: 0 });

  const [origem, setOrigem] = useState('');
  const [destino, setDestino] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resMetricas, resGrafo] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/metricas'),
          axios.get('http://127.0.0.1:5000/api/grafo')
        ]);
        setMetricas(resMetricas.data);
        setDadosGrafo(resGrafo.data);
      } catch (error) {
        console.error("Erro ao buscar dados do Flask:", error);
      }
    };
    fetchData();
  }, []);

  const handleBuscarCaminho = async (origemBusca: string, destinoBusca: string, algoritmo: string) => {
    try {
      const res = await axios.post('http://127.0.0.1:5000/api/caminho', {
        origem: origemBusca, destino: destinoBusca, algoritmo
      });
      setResultado(res.data);
    } catch (error) {
      console.error("Erro ao buscar caminho:", error);
      alert("Erro ao calcular caminho. Verifique se os nós estão corretos.");
    }
  };

  return (
    <Router>
      <div className="flex flex-col h-screen bg-darkbg text-white font-sans overflow-hidden">
        <header className="flex items-center justify-between p-4 bg-darkcard border-b border-gray-800 h-16 flex-shrink-0">
          <div className="flex items-center gap-4">
            <div className="bg-imdb text-black font-black text-2xl px-2 py-1 rounded">IMDb</div>
          </div>
          <nav className="flex gap-6 font-semibold">
            <Link to="/" className="hover:text-imdb transition">Início</Link>
            <Link to="/grafo" className="hover:text-imdb transition">Grafo</Link>
            <Link to="/avd" className="hover:text-imdb transition">AVD</Link>
            <Link to="/filmes" className="hover:text-imdb transition">Filmes</Link>
          </nav>
        </header>

        <main className="flex flex-1 overflow-hidden w-full h-[calc(100vh-4rem)]">
          <Routes>
            <Route path="/" element={<Home />} />
            
            <Route path="/grafo" element={
              <>
                <PainelMetricas 
                  metricas={metricas} 
                  nosDisponiveis={dadosGrafo.nodes}
                  onBuscar={handleBuscarCaminho}
                  resultado={resultado}
                  origem={origem} 
                  setOrigem={setOrigem} 
                  destino={destino} 
                  setDestino={setDestino} 
                />
                <div className="flex-1 h-full relative overflow-hidden p-4">
                  <GrafoInterativo 
                    dadosGrafo={dadosGrafo} 
                    caminho={resultado.caminho} 
                    setOrigem={setOrigem} 
                    setDestino={setDestino} 
                  />
                </div>
              </>
            } />
            
            <Route path="/avd" element={<AVDDashboard />} />
            <Route path="/filmes" element={<div className="flex flex-1 items-center justify-center text-2xl">Aba de Filmes (Em breve)</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}