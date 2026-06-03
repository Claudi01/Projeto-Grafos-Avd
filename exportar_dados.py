import pandas as pd
import json
import os

def exportar_para_json():
    # Caminhos
    path_airports = "parte1/data/aeroportos_data.csv"
    path_degrees = "parte1/out/graus.csv"
    path_passengers = "parte1/data/passageiros.csv"
    path_out = "frontend/public/dados_dashboard.json"

    # Merge
    df_airports = pd.read_csv(path_airports)
    df_degrees = pd.read_csv(path_degrees)
    df_passengers = pd.read_csv(path_passengers)
    
    df = df_passengers.merge(df_airports[['iata', 'regiao', 'cidade']], on='iata', how='left')
    df = df.merge(df_degrees, left_on='iata', right_on='aeroporto', how='left').fillna(0)

    # Converter para lista de dicionários (JSON)
    dados = df.to_dict(orient='records')

    # Salvar na pasta public do React
    if not os.path.exists('frontend/public'):
        os.makedirs('frontend/public')
        
    with open(path_out, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Dados exportados com sucesso para {path_out}")

if __name__ == "__main__":
    exportar_para_json()