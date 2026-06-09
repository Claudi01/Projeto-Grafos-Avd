# Notas Analíticas das Visualizações

## 1. Histograma da Distribuição de Graus

**Arquivo:** `out/histograma_graus.png`

**Tipo:** visualização exploratória.

Esta visualização mostra como os graus dos aeroportos estão distribuídos no grafo. O grau representa a quantidade de conexões diretas de cada aeroporto. O histograma permite observar se a rede possui muitos aeroportos com baixa conectividade ou se há concentração em aeroportos com alto número de conexões. Esse tipo de gráfico foi escolhido porque é adequado para representar a distribuição de uma variável numérica.

## 2. Ranking dos Aeroportos Mais Conectados

**Arquivo:** `out/ranking_graus.png`

**Tipo:** visualização explanatória.

Esta visualização apresenta os aeroportos com maior grau no grafo. O gráfico de barras facilita a identificação dos principais hubs estruturais da rede. A mensagem principal é destacar quais aeroportos concentram mais conexões diretas e, portanto, exercem maior papel de integração no modelo construído.

## 3. Densidade dos Subgrafos por Região

**Arquivo:** `out/densidade_regioes.png`

**Tipo:** visualização exploratória e comparativa.

Esta visualização compara a densidade interna dos subgrafos regionais. A densidade indica o quanto os aeroportos de uma mesma região estão conectados entre si em relação ao máximo possível de conexões. O gráfico de barras foi escolhido porque permite comparar categorias regionais de forma direta e legível.

## 4. Histograma da Densidade das Ego-Networks

**Arquivo:** `out/histograma_ego_densidade.png`

**Tipo:** visualização exploratória.

Esta visualização mostra a distribuição das densidades ego dos aeroportos. A densidade ego mede o nível de conectividade local formado por um aeroporto e seus vizinhos diretos. O histograma permite analisar se a rede possui muitos aeroportos inseridos em vizinhanças locais densas ou se predominam ego-redes menos conectadas.

## 5. Top Aeroportos por Densidade Ego

**Arquivo:** `out/top_ego_densidade.png`

**Tipo:** visualização explanatória.

Esta visualização destaca os aeroportos com maior densidade ego. Diferentemente do grau, que mede apenas o número de conexões diretas, a densidade ego mostra se os vizinhos de um aeroporto também estão conectados entre si. Assim, essa visualização ajuda a identificar aeroportos localizados em subestruturas locais mais coesas.

## 6. Camadas BFS a partir de Recife

**Arquivo:** `out/camadas_bfs_rec.png`

**Tipo:** visualização explanatória.

Esta visualização mostra a distância estrutural dos aeroportos em relação a Recife, considerando o número de arestas necessárias para alcançar cada nó. A BFS percorre o grafo em camadas, tornando essa visualização adequada para representar níveis de alcance dentro da rede.

## 7. Árvore de Percurso das Rotas Obrigatórias

**Arquivo:** `out/arvore_percurso.png`

**Tipo:** visualização obrigatória de percurso.

Esta visualização apresenta os caminhos mínimos calculados pelo algoritmo de Dijkstra para as rotas Recife → Porto Alegre e Manaus → São Paulo. O objetivo é evidenciar a sequência de aeroportos percorrida e o custo total acumulado, considerando os pesos definidos no arquivo de adjacências.
