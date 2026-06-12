# Projeto de Teoria dos Grafos e AVD

A raiz do projeto foi dividida de maneira modular entre `parte1` e `parte2`. Essa separação permitiu a atuação eficiente em subequipes isoladas, garantindo a integridade e independência de cada etapa.

---

## Parte 1: Análise Estrutural da Malha Aérea Brasileira

A **Parte 1** tem como foco a modelagem matemática, análise topológica e visualização de dados (AVD) da infraestrutura de aviação comercial do Brasil. 

Nesta etapa, a malha de aeroportos foi modelada como um Grafo Ponderado Não-Direcionado, utilizando as distâncias geográficas reais em quilômetros como peso das arestas. O projeto processa esses dados de rotas, aplica algoritmos de travessia e de caminhos mínimos (BFS, DFS, Dijkstra, Bellman-Ford) e consolida os resultados em um Dashboard analítico responsivo e um mapa cartográfico interativo.

### Relatório Técnico e Manual
Toda a documentação técnica (incluindo a modelagem, limitações, decisões de UI/UX, leis da Gestalt aplicadas e o guia de operação completo) está detalhada no relatório oficial do projeto.
 **Você pode encontrá-lo em:**
 ```bash
`parte1/relatorio/`
```
### Como Rodar a Parte 1 localmente

A Parte 1 utiliza um backend leve em Flask (Python) para injetar os cálculos em uma interface nativa (HTML, CSS e JavaScript). Siga os passos abaixo:

**1. Instale as dependências gerais**
No terminal, abra a raiz do repositório e instale as bibliotecas requeridas:
```bash
pip install -r requirements.txt
```
2. Navegue para o ambiente da Parte 1:
```bash
cd parte1
```
3. Processe as métricas do Grafo
Antes de iniciar a interface gráfica, execute o motor de processamento. Este script lê os dados em .csv, processa os algoritmos pesados de travessia, constrói a árvore de caminhos e gera os gráficos estáticos que vão para o Dashboard.:
```bash
python -m src.solve
```
4. Inicie o Servidor da Aplicação
Agora, inicie o backend Flask que servirá a plataforma web:
```bash
python -m src.api.app
```
5. Acesse a plataforma
Assim que o terminal indicar que o servidor está rodando, abra o seu navegador e acesse:
```bash
http://127.0.0.1:5000/
```


## Parte 2: Grafo de Filmes Interativo (TMDB)

A raiz da parte 2 e subdividida em duas pastas independentes: backend e frontend. Essa divisao isola a camada de apresentacao em React da camada de servicos em Python, facilitando a manutencao e organizacao do ecossistema, ja que o react gera muitos arquivos utilitarios soltos.

---


### Relatório Técnico e Manual
Toda a documentação técnica (incluindo a modelagem, limitações, decisões de UI/UX, leis da Gestalt aplicadas e o guia de operação completo) está detalhada no relatório oficial do projeto.
 **Você pode encontrá-lo em:**
 ```bash
`parte2/relatorios/`
```

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
