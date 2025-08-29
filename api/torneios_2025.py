import requests
import csv

# Lista de torneios que você quer buscar
tournament_ids = ["339", "336", "8998", "301", "580", "375", "424", "407", "496", "499", "506", "451", "6932", "495", "807", "8996", "404", "403", "717", "360", "4462", "410", "425", "308", "1536", "416", "414", "322", "520", "321", "440", "311", "500", "8994", "741", "540", "7480", "314", "316", "439", "418", "319", "421", "422", "6242"] 

# Cabeçalhos da API
headers = {
    "x-rapidapi-key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "x-rapidapi-host": "ultimate-tennis1.p.rapidapi.com"
}

# Arquivo CSV de saída
output_file = "resultados_torneios.csv"

# Definindo os campos que vão no CSV
fields = [
    "Tournament ID", "Year", "Round", "Location",
    "Winner", "Winner ID", "Loser", "Loser Id",
    "Match Length", "1st Set", "2nd Set", "3rd Set", "4th Set", "5th Set"
]

# Criar CSV e escrever cabeçalho
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    # Loop pelos torneios
    for tid in tournament_ids:
        url = f"https://ultimate-tennis1.p.rapidapi.com/tournament_results/{tid}/2025"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erro na API para torneio {tid}: {response.status_code}")
            continue

        data = response.json()

        # Pode ter vários jogos dentro de um torneio
        for match in data.get("data", []):
            row = {
                "Tournament ID": data.get("Tournament ID"),
                "Year": data.get("Year"),
                "Round": match.get("Round"),
                "Location": match.get("Location"),
                "Winner": match.get("Winner"),
                "Winner ID": match.get("Winner ID"),
                "Loser": match.get("Loser"),
                "Loser Id": match.get("Loser Id"),
                "Match Length": match.get("Match Length"),
                "1st Set": match.get("1st Set"),
                "2nd Set": match.get("2nd Set"),
                "3rd Set": match.get("3rd Set"),
                "4th Set": match.get("4th Set"),
                "5th Set": match.get("5th Set"),
            }
            writer.writerow(row)

print(f"✅ Resultados salvos em {output_file}")
