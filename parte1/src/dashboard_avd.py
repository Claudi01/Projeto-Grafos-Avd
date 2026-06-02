import os
import pandas as pd
import plotly.express as px

def gerar_app_completa():
    path_airports = "parte1/data/aeroportos_data.csv"
    path_degrees = "parte1/out/graus.csv"
    path_passengers = "parte1/data/passageiros.csv"
    path_out = "parte1/out/app_completa.html" 

    if not os.path.exists(path_passengers):
        print(f"Erro: Arquivo {path_passengers} não encontrado.")
        return

    df_airports = pd.read_csv(path_airports)
    df_degrees = pd.read_csv(path_degrees)
    df_passengers = pd.read_csv(path_passengers)

    df_merged = df_passengers.merge(df_airports[['iata', 'regiao', 'cidade']], on='iata', how='left')
    df_merged = df_merged.merge(df_degrees, left_on='iata', right_on='aeroporto', how='left').fillna(0)

    total_passageiros = df_merged['passageiros_milhoes'].sum()
    top_hub_nome = df_merged.loc[df_merged['grau'].idxmax(), 'iata']
    top_hub_grau = df_merged['grau'].max()
    top_trafego_nome = df_merged.loc[df_merged['passageiros_milhoes'].idxmax(), 'iata']

    cores_regioes = {'Norte': '#2ca02c', 'Nordeste': '#ff7f0e', 'Centro-Oeste': '#d62728', 'Sudeste': '#1f77b4', 'Sul': '#9467bd'}
    
    fig = px.scatter(
        df_merged, x="grau", y="passageiros_milhoes", size="passageiros_milhoes", color="regiao",
        color_discrete_map=cores_regioes, hover_name="iata",
        custom_data=["cidade", "regiao"], 
        labels={"grau": "Conexões Estruturais (Grau)", "passageiros_milhoes": "Passageiros Anuais (Milhões)"},
        size_max=55, template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, title_text=""),
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)", font_size=13, font_family="Inter",
            font_color="#0f172a", bordercolor="rgba(0,0,0,0.2)"
        ),
        xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False),
    )
    
    fig.update_traces(
        marker=dict(line=dict(width=1.5, color='rgba(255, 255, 255, 0.8)'), opacity=0.85),
        hovertemplate=(
            "<b style='font-size: 15px;'>✈️ Aeroporto: %{hovertext}</b><br><br>"
            "📍 <b>Cidade:</b> %{customdata[0]}<br>"
            "🗺️ <b>Região:</b> %{customdata[1]}<br>"
            "🔗 <b>Conexões (Grau):</b> %{x}<br>"
            "👥 <b>Tráfego:</b> %{y} Milhões<br>"
            "<extra></extra>"
        )
    )

    config_plotly = {'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d']}
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn', config=config_plotly)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>App Aviação</title>
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
                display: flex; flex-direction: column; gap: 1.5rem;
            }}
            
            header {{ text-align: center; margin-bottom: 0.5rem; }}
            header h1 {{ font-size: 2.2rem; font-weight: 700; background: -webkit-linear-gradient(#93c5fd, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            header p {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 0.5rem; }}

            .tab-container {{
                display: flex; justify-content: center; gap: 1rem; margin-bottom: 1rem;
            }}
            .tab-btn {{
                background: var(--glass-bg); border: 1px solid var(--glass-border);
                color: var(--text-main); padding: 0.8rem 2rem; border-radius: 8px;
                font-size: 1rem; cursor: pointer; transition: all 0.3s ease;
                backdrop-filter: blur(16px); font-weight: 500; display: flex; align-items: center; gap: 0.5rem;
            }}
            .tab-btn:hover {{ background: rgba(59, 130, 246, 0.1); transform: translateY(-2px); }}
            .tab-btn.active {{
                background: rgba(59, 130, 246, 0.2); border-color: var(--accent);
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); color: #fff;
            }}

            .tab-content {{ display: none; flex-direction: column; gap: 1.5rem; }}
            .tab-content.active {{ display: flex; animation: fadeIn 0.5s ease-out; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(15px); }} to {{ opacity: 1; transform: translateY(0); }} }}

            .kpi-container {{ display: flex; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; }}
            .kpi-card {{
                flex: 1; min-width: 220px; background: var(--glass-bg); backdrop-filter: blur(16px);
                border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.5rem; text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease;
            }}
            .kpi-card:hover {{ transform: translateY(-5px); border-color: rgba(96, 165, 250, 0.5); }}
            .kpi-title {{ font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem; }}
            .kpi-value {{ font-size: 2rem; font-weight: 700; color: var(--text-main); }}
            .kpi-value span {{ font-size: 1.1rem; font-weight: 300; color: var(--accent); }}

            .chart-container {{
                background: var(--glass-bg); backdrop-filter: blur(16px);
                border: 1px solid var(--glass-border); border-radius: 12px;
                padding: 1rem 1.5rem; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                flex-grow: 1; display: flex; flex-direction: column;
            }}

            .iframe-container {{ 
                height: 85vh; /* Ocupa 85% da tela */
                min-height: 760px; /* Impede que o grafo seja cortado */
                width: 100%;
                padding: 0; 
                overflow: hidden; 
                border-radius: 16px;
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
                background-color: #1e1e1e; /* Mesma cor base do pyvis */
            }}
            iframe {{ width: 100%; height: 100%; border: none; border-radius: 16px; }}

            .fonte-dados {{
                text-align: center; font-size: 0.85rem; color: var(--text-muted);
                font-style: italic; margin-top: 0.5rem; opacity: 0.8;
            }}
        </style>
    </head>
    <body>

        <header>
            <h1>Plataforma: Aviação</h1>
            <p>Integração de Modelagem de Grafos e Análise Visual de Dados</p>
        </header>

        <div class="tab-container">
            <button class="tab-btn active" onclick="switchTab(event, 'tab-avd')">Dashboard (AVD)</button>
            <button class="tab-btn" onclick="switchTab(event, 'tab-grafo')">Grafo Interativo (Grafos)</button>
        </div>

        <div id="tab-avd" class="tab-content active">
            <div class="kpi-container">
                <div class="kpi-card">
                    <div class="kpi-title">Tráfego Total Analisado</div>
                    <div class="kpi-value">{total_passageiros:.1f} <span>Milhões</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Maior Hub Estrutural (Grau)</div>
                    <div class="kpi-value">{top_hub_nome} <span>({int(top_hub_grau)} rotas)</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Maior Tráfego de Passageiros</div>
                    <div class="kpi-value">{top_trafego_nome} <span>(Pico)</span></div>
                </div>
            </div>
            <div class="chart-container">
                {graph_html}
            </div>
            <div class="fonte-dados">
                Fonte dos Dados de Tráfego: Agência Nacional de Aviação Civil (ANAC)
            </div>
        </div>

        <div id="tab-grafo" class="tab-content">
            <div class="iframe-container">
                <iframe src="grafo_interativo.html" title="Grafo Interativo"></iframe>
            </div>
        </div>

        <script>
            function switchTab(evt, tabId) {{
                var contents = document.getElementsByClassName("tab-content");
                for (var i = 0; i < contents.length; i++) {{
                    contents[i].classList.remove("active");
                }}
                var btns = document.getElementsByClassName("tab-btn");
                for (var i = 0; i < btns.length; i++) {{
                    btns[i].classList.remove("active");
                }}
                document.getElementById(tabId).classList.add("active");
                evt.currentTarget.classList.add("active");
            }}
        </script>
    </body>
    </html>
    """

    with open(path_out, "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    gerar_app_completa()