import { useState, useMemo, useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

interface Node {
  id: string | number;
  label?: string;
  [key: string]: any;
}

interface Link {
  source: string | number | any;
  target: string | number | any;
  weight?: number;
  [key: string]: any;
}

interface GrafoInterativoProps {
  dadosGrafo: {
    nodes: Node[];
    links: Link[];
  };
  caminho: string[];
}

export default function GrafoInterativo({ dadosGrafo, caminho }: GrafoInterativoProps) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  const neighbors = useMemo(() => {
    const map = new Map();
    dadosGrafo.links.forEach(link => {
      const source = String(typeof link.source === 'object' ? link.source.id : link.source); 
      const target = String(typeof link.target === 'object' ? link.target.id : link.target); 
      if (!map.has(source)) map.set(source, new Set());
      if (!map.has(target)) map.set(target, new Set());
      map.get(source).add(target);
      map.get(target).add(source);
    });
    return map;
  }, [dadosGrafo]);

  return (
    <div ref={containerRef} className="relative w-full h-full bg-black rounded-lg overflow-hidden border border-gray-800">
      <ForceGraph2D
        width={dimensions.width}
        height={dimensions.height}
        graphData={dadosGrafo}
        nodeLabel="label"
        nodeVal={(node: any) => node.val || 1.5} 
        enableNodeDrag={false}
        onNodeClick={(node) => setSelectedNode(node === selectedNode ? null : node)}
        nodeColor={(node) => {
          const nodeId = String(node.id); 
          if (caminho.includes(nodeId)) return '#ff0000';
          
          if (selectedNode) {
            const selectedId = String(selectedNode.id); 
            const isNeighbor = neighbors.get(selectedId)?.has(nodeId);
            return nodeId === selectedId || isNeighbor ? '#f5c518' : 'rgba(245, 197, 24, 0.2)';
          }
          return '#f5c518';
        }}
        linkColor={(link) => {
          const sourceId = String(typeof link.source === 'object' ? link.source.id : link.source); 
          const targetId = String(typeof link.target === 'object' ? link.target.id : link.target); 
          const noCaminho = caminho.includes(sourceId) && caminho.includes(targetId);
          
          if (noCaminho) return '#ff0000';

          if (selectedNode) {
            const selectedId = String(selectedNode.id); 
            const isConnected = sourceId === selectedId || targetId === selectedId;
            return isConnected ? 'rgba(255, 255, 255, 0.8)' : 'rgba(51, 51, 51, 0.1)';
          }
          return '#333333';
        }}
        linkWidth={(link) => {
          const sourceId = String(typeof link.source === 'object' ? link.source.id : link.source);
          const targetId = String(typeof link.target === 'object' ? link.target.id : link.target);
          return caminho.includes(sourceId) && caminho.includes(targetId) ? 3 : 1;
        }}
        backgroundColor="#000000"
      />

      {selectedNode && (
        <div className="absolute right-4 top-4 bottom-4 w-80 bg-darkcard bg-opacity-95 backdrop-blur-sm p-4 border border-gray-800 rounded-lg flex flex-col gap-4 z-10 shadow-2xl">
          <h2 className="text-2xl font-bold text-imdb">{selectedNode.label || 'Título Desconhecido'}</h2>
          <p className="text-sm text-gray-400">ID: {selectedNode.id}</p>
          
          <div className="flex-1">
            <div className="w-full h-40 bg-gray-800 rounded flex items-center justify-center text-gray-500">
              Trailer (Em breve)
            </div>
          </div>
          
          <button 
            onClick={() => setSelectedNode(null)}
            className="mt-auto px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition font-semibold"
          >
            Fechar
          </button>
        </div>
      )}
    </div>
  );
}