import csv
import time
import os 
import requests
from pathlib import Path
from dotenv import load_dotenv 

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_youtube_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for video in results:
                if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                    return video.get("key")
    except Exception as e:
        print(f"Erro ao buscar filme {movie_id}: {e}")
    return ""

def main():
    if not TMDB_API_KEY:
        print("Erro: TMDB_API_KEY não encontrada no ficheiro .env")
        return

    base_dir = Path(__file__).resolve().parent.parent / "data"
    input_csv = base_dir / "tmdb_5000_credits.csv"
    output_csv = base_dir / "tmdb_5000_credits_com_trailer.csv"

    if not input_csv.exists():
        print(f"Arquivo não encontrado: {input_csv}")
        return

    with open(input_csv, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["youtube_trailer_key"]
        
        filmes = list(reader)

    print(f"Iniciando busca de trailers para {len(filmes)} filmes. Isso levará alguns minutos...")

    with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, row in enumerate(filmes):
            movie_id = row["movie_id"]
            trailer_key = fetch_youtube_trailer(movie_id)
            
            row["youtube_trailer_key"] = trailer_key
            writer.writerow(row)

            time.sleep(0.05) 
            
            if (idx + 1) % 100 == 0:
                print(f"Progresso: {idx + 1}/{len(filmes)} filmes processados...")

    print(f"Concluído! Novo dataset salvo em: {output_csv}")

if __name__ == "__main__":
    main()