# stats.py
import requests
import os
import json # Importar json para pretty print na depuração
from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

STATS_RAPIDAPI_KEY = os.getenv("STATS_RAPIDAPI_KEY", os.getenv("RAPIDAPI_KEY"))
STATS_RAPIDAPI_HOST = os.getenv("STATS_RAPIDAPI_HOST", "ultimate-tennis1.p.rapidapi.com")

DESIRED_STATS_COLUMNS = {
    "PlayerId": "player_id",
    "PlayerName": "player_name_raw",
    "AvgAcesPerMatchSortField": "avg_aces_match",
    "AvgDblFaultsPerMatchSortField": "avg_dbl_faults_match",
    "FirstServePctSortField": "first_serve_pct",
    "FirstServePointsWonPctSortField": "first_serve_points_won_pct",
    "SecondServePointsWonPctSortField": "second_serve_points_won_pct",
    "ServeRatingSortField": "serve_rating",
    "ServiceGamesWonPctSortField": "service_games_won_pct"
}

def normalize_player_name(name):
    if not name:
        return ""
    name = name.lower()
    if ',' in name:
        parts = name.split(',', 1)
        name = f"{parts[1].strip()} {parts[0].strip()}"
    name = ''.join(char for char in name if char.isalnum() or char.isspace())
    name = ' '.join(name.split())
    return name

def get_all_player_stats(year="2024"):
    url = f"https://{STATS_RAPIDAPI_HOST}/global_players_stats/serve/{year}/all"
    headers = {
        "x-rapidapi-key": STATS_RAPIDAPI_KEY,
        "x-rapidapi-host": STATS_RAPIDAPI_HOST
    }

    print(f"\nBuscando estatísticas de jogadores para o ano {year}...")
    all_player_stats_map = {}
    request_count = 0

    try:
        response = requests.get(url, headers=headers)
        request_count += 1
        response.raise_for_status()
        raw_response_data = response.json()

        actual_player_list = []

        if isinstance(raw_response_data, list):
            actual_player_list = raw_response_data
            print(f"  API de estatísticas retornou uma lista diretamente com {len(actual_player_list)} itens.")
        elif isinstance(raw_response_data, dict):
            print(f"  API de estatísticas retornou um dicionário. Tentando encontrar a lista de jogadores dentro dele.")
            # Imprime o dicionário para ajudar na depuração e identificar a chave correta
            print(f"  Conteúdo do dicionário da API de estatísticas: {json.dumps(raw_response_data, indent=2)}")

            possible_keys = ['data', 'results', 'players', 'items', 'statistics', 'response'] # Chaves comuns
            found_list = False
            for key in possible_keys:
                if key in raw_response_data and isinstance(raw_response_data[key], list):
                    actual_player_list = raw_response_data[key]
                    print(f"  Lista de jogadores encontrada sob a chave '{key}' no dicionário (contém {len(actual_player_list)} itens).")
                    found_list = True
                    break

            if not found_list:
                print(f"  Não foi possível encontrar uma lista de jogadores dentro das chaves comuns do dicionário retornado.")
                if raw_response_data.get("message"):
                    print(f"  Mensagem da API de Estatísticas: {raw_response_data.get('message')}")
                # Se a API retorna um dicionário sem uma lista de jogadores óbvia,
                # e não é uma mensagem de erro conhecida, pode ser que a própria raiz do dicionário
                # seja o dado de um único jogador, ou uma estrutura diferente.
                # Por enquanto, vamos tratar como se não houvesse dados de jogadores.
                return {}, request_count
        else:
            print(f"  Formato inesperado para dados de estatísticas: {type(raw_response_data)}. Esperava lista ou dicionário.")
            return {}, request_count

        if not actual_player_list:
            print("  Nenhum dado de jogador utilizável encontrado na resposta da API de estatísticas.")
            return {}, request_count

        processed_count = 0
        for player_data in actual_player_list:
            if not isinstance(player_data, dict):
                # print(f"  Item de estatística de jogador não é um dicionário: {player_data}")
                continue

            stats = {}
            for api_key, new_key in DESIRED_STATS_COLUMNS.items():
                stats[new_key] = player_data.get(api_key)

            if stats.get("player_name_raw"):
                normalized_name = normalize_player_name(stats["player_name_raw"])
                if normalized_name:
                    all_player_stats_map[normalized_name] = stats
                    processed_count += 1

        if processed_count > 0:
            print(f"  Estatísticas de {processed_count} jogadores processadas e mapeadas.")
        else:
            print("  Nenhum jogador foi processado a partir da lista obtida.")

        return all_player_stats_map, request_count

    except requests.exceptions.HTTPError as http_err:
        print(f"  Erro HTTP ao buscar estatísticas de jogadores: {http_err}")
        print(f"  Conteúdo da resposta (se houver): {response.text}")
        return {}, request_count
    except requests.exceptions.RequestException as e:
        print(f"  Erro de requisição ao buscar estatísticas de jogadores: {e}")
        return {}, request_count
    except ValueError:
        print(f"  Erro ao decodificar JSON da resposta de estatísticas. Resposta: {response.text if 'response' in locals() else 'N/A'}")
        return {}, request_count

if __name__ == "__main__":
    if not STATS_RAPIDAPI_KEY or STATS_RAPIDAPI_KEY == "SUA_CHAVE_API_AQUI" or not STATS_RAPIDAPI_HOST :
         print("Chave/Host da API de estatísticas não configurada no .env ou no script para teste.")
    else:
        player_stats_map, req_count = get_all_player_stats()
        print(f"Total de requisições à API de estatísticas: {req_count}")
        if player_stats_map:
            print(f"\nEncontradas estatísticas para {len(player_stats_map)} jogadores.")
            sample_name = next(iter(player_stats_map))
            print(f"\nExemplo de estatísticas para '{sample_name}':")
            print(json.dumps(player_stats_map[sample_name], indent=2))
            print("\nTestando normalização:")
            names_to_test = ["Djokovic, Novak", "Novak Djokovic", "Carlos Alcaraz", "Alcaraz, Carlos"]
            for name in names_to_test:
                norm_name = normalize_player_name(name)
                print(f"'{name}' -> '{norm_name}' -> Stats found: {bool(player_stats_map.get(norm_name))}")
        else:
            print("Nenhuma estatística de jogador foi carregada.")