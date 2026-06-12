# Projeto de teoria dos grafos e AVD


A raiz do projeto foi dividida de maneira modular entre parte1 e parte2. Essa separacao permitiu a atuacao eficiente em subequipes isoladas, garantindo que o progresso de cada etapa ocorresse de forma simultanea sem a ocorrencia de conflitos de mesclagem ou interferencias mutuas no codigo-fonte.

A raiz da parte 2 e subdividida em duas pastas independentes: backend e frontend. Essa divisao isola a camada de apresentacao em React da camada de servicos em Python, facilitando a manutencao e organizacao do ecossistema, ja que o react gera muitos arquivos utilitarios soltos.

---

## Instrucoes de Instalacao e Execucao

### Back-end (Python e Flask)

O back-end armazena o dataset, constroi a lista de adjacencias do grafo do zero e disponibiliza endpoints de API REST para o funcionamento da aplicacao.

1. Navegue ate o diretorio do back-end:
cd parte2/backend

2. Instale as dependencias necessarias:
pip install pandas flask flask-cors pytest

3. Execute o script de geracao do relatorio global (solve.py). Este script realiza o processamento massivo de rotas reais na rede para alimentar o painel estatistico:
python -m src.solve

4. Inicialize o servidor Flask para conexao com a interface grafica:
python -m src.app

---

### Front-end (React, Vite e Recharts)

O front-end renderiza a malha de conexoes de forma estatica a partir do layout calculado no servidor e apresenta um painel de benchmarking visual para inspecao dos algoritmos.

1. Abra um novo terminal e navegue ate o diretorio do front-end:
cd parte2/frontend

2. Instale as dependencias base do projeto:
npm install

3. Instale a biblioteca de graficos Recharts necessaria para renderizar o painel de analise visual:
npm install recharts

4. Inicie a aplicacao em modo de desenvolvimento local:
npm run dev

Abra o navegador no endereco indicado no terminal (normalmente http://localhost:5173).

---

## Procedimentos de Auditoria e Testes

### Execucao via Linha de Comando (CLI)

Para testar consultas customizadas e algoritmos individuais diretamente pelo terminal do back-end, utilize o modulo cli.py fornecendo as flags obrigatorias. O parametro --out e opcional e serve para salvar a resposta estruturada na pasta out:

python -m src.cli --algoritmo DIJKSTRA --origem "The Matrix" --destino "Avatar" --out ./out/

Opcoes validas para a flag --algoritmo: BFS, DFS, DIJKSTRA, BELLMAN-FORD.

### Execucao da Suite de Testes Automatizados

Para fins de validacao das regras de consistencia logica exigidas na rubrica — como os niveis da busca em largura, a profundidade da busca em profundidade, a rejeicao de pesos negativos no Dijkstra e a interrupcao preventiva do Bellman-Ford em ciclos negativos —, execute a suite de testes automatizados com o pytest a partir da pasta backend:

python -m pytest
