import os
import pandas as pd
import plotly.express as px

def gerar_app_completa():
    # 1. Carregamento
    path_airports = "parte1/data/aeroportos_data.csv"
    path_degrees = "parte1/out/graus.csv"
    path_passengers = "parte1/data/passageiros.csv"
    path_ego = "parte1/out/ego_aeroportos.csv"
    path_out = "parte1/out/app_completa.html" 

    if not os.path.exists(path_passengers):
        print(f"Erro: Arquivo {path_passengers} não encontrado.")
        return

    df_airports = pd.read_csv(path_airports)
    df_degrees = pd.read_csv(path_degrees)
    df_passengers = pd.read_csv(path_passengers)
    df_ego = pd.read_csv(path_ego) if os.path.exists(path_ego) else pd.DataFrame(columns=['aeroporto', 'densidade_ego'])

    # 2. ENGENHARIA DE DADOS: Faxina Pesada (Garante que os Gráficos nunca fiquem em branco)
    # Removemos espaços em branco fantasmas e forçamos tudo para maiúsculo para o Merge ser perfeito
    df_airports['iata'] = df_airports['iata'].astype(str).str.strip().str.upper()
    df_passengers['iata'] = df_passengers['iata'].astype(str).str.strip().str.upper()
    
    if not df_degrees.empty:
        df_degrees['aeroporto'] = df_degrees['aeroporto'].astype(str).str.strip().str.upper()
    if not df_ego.empty:
        df_ego['aeroporto'] = df_ego['aeroporto'].astype(str).str.strip().str.upper()

    df_merged = df_airports[['iata', 'regiao', 'cidade']].copy()
    df_merged['regiao'] = df_merged['regiao'].fillna('Desconhecida').astype(str).str.strip()
    df_merged['cidade'] = df_merged['cidade'].fillna('Desconhecida').astype(str).str.strip()

    # União das Tabelas (Agora os dados batem 100%)
    df_merged = df_merged.merge(df_passengers, on='iata', how='left')
    df_merged = df_merged.merge(df_degrees, left_on='iata', right_on='aeroporto', how='left')
    df_merged = df_merged.merge(df_ego[['aeroporto', 'densidade_ego']], left_on='iata', right_on='aeroporto', how='left')

    # Correção de Tipos (Mata o bug da vírgula decimal brasileira)
    df_merged['passageiros_milhoes'] = df_merged['passageiros_milhoes'].astype(str).str.replace(',', '.')
    df_merged['passageiros_milhoes'] = pd.to_numeric(df_merged['passageiros_milhoes'], errors='coerce').fillna(0.0)

    df_merged['grau'] = pd.to_numeric(df_merged['grau'], errors='coerce').fillna(0).astype(int)
    
    df_merged['densidade_ego'] = df_merged['densidade_ego'].astype(str).str.replace(',', '.')
    df_merged['densidade_ego'] = pd.to_numeric(df_merged['densidade_ego'], errors='coerce').fillna(0.0)

    df_merged = df_merged.sort_values(by='passageiros_milhoes', ascending=False)

    # 3. Métricas (KPIs)
    total_passageiros = df_merged['passageiros_milhoes'].sum()
    total_aeroportos = len(df_merged[df_merged['grau'] > 0])
    top_hub_nome = df_merged.loc[df_merged['grau'].idxmax(), 'iata'] if not df_merged.empty else "-"
    top_hub_grau = df_merged['grau'].max() if not df_merged.empty else 0
    top_trafego_nome = df_merged.loc[df_merged['passageiros_milhoes'].idxmax(), 'iata'] if not df_merged.empty else "-"

    # GESTALT: Cores padronizadas
    cores_regioes = {'Norte': '#2ca02c', 'Nordeste': '#ff7f0e', 'Centro-Oeste': '#d62728', 'Sudeste': '#1f77b4', 'Sul': '#9467bd', 'Desconhecida': '#7f8c8d'}
    layout_base = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#e2e8f0", family="Inter"), margin=dict(l=20, r=20, t=50, b=20), autosize=True)

    # ================= GERADOR DE GRÁFICOS (DESIGN APURADO) =================

    # 1. Visão Macro: Sunburst
    df_macro = df_merged[df_merged['passageiros_milhoes'] > 0.1].copy()
    fig1 = px.sunburst(df_macro, path=['regiao', 'iata'], values='passageiros_milhoes', color='regiao', color_discrete_map=cores_regioes, title="1. Hierarquia de Tráfego (Região > Aeroporto)", template="plotly_dark")
    fig1.update_traces(textinfo="label+percent parent", marker=dict(line=dict(width=1.5, color="#0f172a")))
    fig1.update_layout(**layout_base)

    # 2. Visão Macro: Barras Regionais (Melhorado para nunca cortar os números)
    df_regiao = df_merged.groupby('regiao', as_index=False)['passageiros_milhoes'].sum().sort_values('passageiros_milhoes', ascending=True)
    fig2 = px.bar(df_regiao, x="passageiros_milhoes", y="regiao", color="regiao", color_discrete_map=cores_regioes, orientation='h', text_auto='.1f', title="2. Carga Total por Região (Milhões)", template="plotly_dark")
    fig2.update_layout(**layout_base, showlegend=False, xaxis_title="", yaxis_title="")
    fig2.update_traces(textposition="outside", textfont_size=13, cliponaxis=False)
    fig2.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    # 3. Visão Meso: Dispersão Clássica (Garante que a bolha não suma)
    fig3 = px.scatter(df_merged[df_merged['passageiros_milhoes'] > 0], x="grau", y="passageiros_milhoes", size="passageiros_milhoes", size_max=45, color="regiao", color_discrete_map=cores_regioes, hover_name="iata", title="3. Estrutura (Grau) vs Tráfego", template="plotly_dark")
    fig3.update_layout(**layout_base, xaxis_title="Quantidade de Conexões (Grau)", yaxis_title="Milhões de Passageiros")
    fig3.update_traces(marker=dict(line=dict(width=1, color='rgba(255,255,255,0.8)'), opacity=0.8), cliponaxis=False)
    fig3.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig3.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    # 4. Visão Meso: Violin Plot
    fig4 = px.violin(df_merged[df_merged['passageiros_milhoes'] > 0.05], x="regiao", y="passageiros_milhoes", color="regiao", color_discrete_map=cores_regioes, box=True, title="4. Densidade de Tráfego Regional", template="plotly_dark")
    fig4.update_layout(**layout_base, showlegend=False, xaxis_title="", yaxis_title="Passageiros (Milhões)")
    fig4.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    # 5. Visão Micro: Top 10 Aeroportos
    df_top10 = df_merged.nlargest(10, 'passageiros_milhoes').sort_values('passageiros_milhoes', ascending=True)
    fig5 = px.bar(df_top10, x="passageiros_milhoes", y="iata", color="grau", orientation='h', color_continuous_scale="Viridis", text_auto='.1f', title="5. Top 10 Aeroportos (Cor = Conexões)", template="plotly_dark")
    fig5.update_layout(**layout_base, xaxis_title="Milhões de Passageiros", yaxis_title="", coloraxis_colorbar=dict(title="Grau"))
    fig5.update_traces(textposition="outside", textfont_size=12, cliponaxis=False)
    fig5.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    # 6. Visão Micro: Histograma (Lida perfeitamente com os dados reais)
    fig6 = px.histogram(df_merged[df_merged['grau'] > 0], x="grau", color="regiao", color_discrete_map=cores_regioes, title="6. Frequência da Malha", template="plotly_dark", nbins=15)
    fig6.update_layout(**layout_base, barmode='stack', xaxis_title="Grau (Conexões)", yaxis_title="Quantidade de Aeroportos")
    fig6.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig6.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    # Extração HTML Leve
    config_plotly = {'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d'], 'responsive': True}
    html_f1 = fig1.to_html(full_html=False, include_plotlyjs=False, config=config_plotly, default_width="100%", default_height="100%")
    html_f2 = fig2.to_html(full_html=False, include_plotlyjs=False, config=config_plotly, default_width="100%", default_height="100%")
    html_f3 = fig3.to_html(full_html=False, include_plotlyjs=False, config=config_plotly, default_width="100%", default_height="100%")
    html_f4 = fig4.to_html(full_html=False, include_plotlyjs=False, config=config_plotly, default_width="100%", default_height="100%")
    html_f5 = fig5.to_html(full_html=False, include_plotlyjs=False, config=config_plotly, default_width="100%", default_height="100%")
    html_f6 = fig6.to_html(full_html=False, include_plotlyjs=False, config=config_plotly, default_width="100%", default_height="100%")

    # ================= ESTRUTURA HTML / CSS / JS =================
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>App Integrada - Grafos & AVD</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #0f172a; --glass-bg: rgba(30, 41, 59, 0.4);
                --glass-border: rgba(255, 255, 255, 0.1); --text-main: #f8fafc;
                --text-muted: #94a3b8; --accent: #3b82f6;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
            body {{
                background: linear-gradient(135deg, #020617 0%, #1e1e2f 100%);
                color: var(--text-main); min-height: 100vh; padding: 2rem;
                display: flex; flex-direction: column; gap: 1rem; overflow-x: hidden;
            }}
            header {{ text-align: center; margin-bottom: 0.5rem; }}
            header h1 {{ font-size: 2.2rem; font-weight: 700; background: -webkit-linear-gradient(#93c5fd, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            header p {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 0.5rem; }}
            .tab-container {{ display: flex; justify-content: center; gap: 1rem; margin-bottom: 1rem; }}
            .tab-btn {{
                background: var(--glass-bg); border: 1px solid var(--glass-border); color: var(--text-main); padding: 0.8rem 2rem; border-radius: 8px;
                font-size: 1rem; cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(16px); font-weight: 500; display: flex; align-items: center; gap: 0.5rem;
            }}
            .tab-btn:hover {{ background: rgba(59, 130, 246, 0.1); transform: translateY(-2px); }}
            .tab-btn.active {{ background: rgba(59, 130, 246, 0.2); border-color: var(--accent); box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); color: #fff; }}
            .tab-content {{ display: none; flex-direction: column; gap: 1.5rem; width: 100%; }}
            .tab-content.active {{ display: flex; animation: fadeIn 0.5s ease-out; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(15px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .kpi-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; }}
            .kpi-card {{
                background: var(--glass-bg); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.5rem; text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease;
            }}
            .kpi-card:hover {{ transform: translateY(-5px); border-color: rgba(96, 165, 250, 0.5); }}
            .kpi-title {{ font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem; }}
            .kpi-value {{ font-size: 2rem; font-weight: 700; color: var(--text-main); }}
            .kpi-value span {{ font-size: 1.1rem; font-weight: 300; color: var(--accent); }}
            
            /* CSS GRID Melhorado */
            .chart-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }}
            .chart-card {{
                background: var(--glass-bg); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 12px;
                padding: 1rem; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3); height: 400px; display: flex; flex-direction: column; overflow: visible; /* Permite bordas fluidas */
            }}
            .chart-card.wide {{ grid-column: span 2; height: 480px; }}
            
            .iframe-container {{ 
                height: 85vh; min-height: 760px; width: 100%; padding: 0; overflow: hidden; border-radius: 16px; box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1); background-color: #1e1e1e;
            }}
            iframe {{ width: 100%; height: 100%; border: none; border-radius: 16px; }}
            .fonte-dados {{ text-align: center; font-size: 0.85rem; color: var(--text-muted); font-style: italic; margin-top: 0.5rem; opacity: 0.8; }}
        </style>
    </head>
    <body>
        <header>
            <h1>Plataforma Analítica Multi-Métricas: Aviação</h1>
            <p>Integração de Modelagem de Grafos (Pyvis) e Análise Visual de Dados (Plotly)</p>
        </header>
        <div class="tab-container">
            <button class="tab-btn active" onclick="switchTab(event, 'tab-avd')">📊 Painel Analítico (AVD)</button>
            <button class="tab-btn" onclick="switchTab(event, 'tab-grafo')">🕸️ Malha Interativa (Grafos)</button>
        </div>
        
        <div id="tab-avd" class="tab-content active">
            <div class="kpi-container">
                <div class="kpi-card"><div class="kpi-title">Tráfego Total Analisado</div><div class="kpi-value">{total_passageiros:.1f} <span>Milhões</span></div></div>
                <div class="kpi-card"><div class="kpi-title">Aeroportos Conectados</div><div class="kpi-value">{total_aeroportos} <span>Nós</span></div></div>
                <div class="kpi-card"><div class="kpi-title">Maior Hub Estrutural</div><div class="kpi-value">{top_hub_nome} <span>({int(top_hub_grau)} rotas)</span></div></div>
                <div class="kpi-card"><div class="kpi-title">Pico de Passageiros</div><div class="kpi-value">{top_trafego_nome} <span>(Máx)</span></div></div>
            </div>
            
            <div class="chart-grid">
                <div class="chart-card wide">{html_f1}</div> 
                <div class="chart-card">{html_f2}</div>      
                <div class="chart-card">{html_f3}</div>      
                <div class="chart-card">{html_f4}</div>      
                <div class="chart-card">{html_f5}</div>      
                <div class="chart-card">{html_f6}</div>      
            </div>
            <div class="fonte-dados">Fonte dos Dados de Tráfego: Agência Nacional de Aviação Civil (ANAC)</div>
        </div>
        
        <div id="tab-grafo" class="tab-content">
            <div class="iframe-container">
                <iframe src="grafo_interativo.html" title="Grafo Interativo"></iframe>
            </div>
        </div>
        
        <script>
            function switchTab(evt, tabId) {{
                var contents = document.getElementsByClassName("tab-content");
                for (var i = 0; i < contents.length; i++) contents[i].classList.remove("active");
                var btns = document.getElementsByClassName("tab-btn");
                for (var i = 0; i < btns.length; i++) btns[i].classList.remove("active");
                document.getElementById(tabId).classList.add("active");
                evt.currentTarget.classList.add("active");
                setTimeout(() => {{ window.dispatchEvent(new Event('resize')); }}, 50);
            }}
            window.onload = () => {{ window.dispatchEvent(new Event('resize')); }};
        </script>
    </body>
    </html>
    """

    with open(path_out, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Dashboard Executivo Master gerado em: {path_out}")

if __name__ == "__main__":
    gerar_app_completa()