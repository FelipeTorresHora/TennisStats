import requests
import time
import json
import os
from dotenv import load_dotenv

# Importar funções do stats.py
from stats import get_all_player_stats, normalize_player_name

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Credenciais para API de Odds ---
# Usar nomes específicos para clareza, caso as chaves/hosts sejam diferentes da API de stats
ODDS_RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") # Sua chave principal para a API de Odds
ODDS_RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST") # Host da API de Odds

# Headers base para a API de Odds
# É importante que estes sejam para a API de Odds
BASE_HEADERS = {
    "x-rapidapi-key": ODDS_RAPIDAPI_KEY,
    "x-rapidapi-host": ODDS_RAPIDAPI_HOST
}

# --- Funções da API de Odds (get_tournaments, get_events, get_odds, process_odds_data) ---
# Estas funções permanecem como você as desenvolveu e testou.
# A única mudança potencial seria aceitar um parâmetro 'headers' se você refatorar
# para não usar BASE_HEADERS globalmente.

def get_tournaments(sport="tennis"): # Adicionar headers como parâmetro se refatorar
    url = f"https://{ODDS_RAPIDAPI_HOST}/tournaments" # Usar ODDS_RAPIDAPI_HOST
    querystring = {"sport": sport}
    try:
        # Passar BASE_HEADERS (ou o parâmetro de headers se refatorado)
        response = requests.get(url, headers=BASE_HEADERS, params=querystring)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar torneios: {e}")
        return None, False
    except ValueError:
        print(f"Erro ao decodificar JSON da resposta de torneios. Resposta: {response.text}")
        return None, False

def get_events(tournament_id, media="false"): # Adicionar headers como parâmetro se refatorar
    url = f"https://{ODDS_RAPIDAPI_HOST}/events" # Usar ODDS_RAPIDAPI_HOST
    querystring = {"tournamentId": tournament_id, "media": media}
    try:
        # Passar BASE_HEADERS (ou o parâmetro de headers se refatorado)
        response = requests.get(url, headers=BASE_HEADERS, params=querystring)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar eventos para o torneio {tournament_id}: {e}")
        return None, False
    except ValueError:
        print(f"Erro ao decodificar JSON da resposta de eventos. Resposta: {response.text}")
        return None, False

def get_odds(event_id, bookmakers="bet365", odds_format="decimal", raw="false"): # Adicionar headers como parâmetro se refatorar
    url = f"https://{ODDS_RAPIDAPI_HOST}/odds" # Usar ODDS_RAPIDAPI_HOST
    querystring = {
        "eventId": event_id,
        "bookmakers": bookmakers,
        "oddsFormat": odds_format,
        "raw": raw
    }
    try:
        # Passar BASE_HEADERS (ou o parâmetro de headers se refatorado)
        response = requests.get(url, headers=BASE_HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'markets' not in data and data.get('message'):
            print(f"      Mensagem da API de odds para o evento {event_id} (bookmaker: {bookmakers}): {data['message']}")
            return None, True
        elif isinstance(data, list) and not data:
             print(f"      API de odds retornou uma lista vazia para o evento {event_id} (bookmaker: {bookmakers}).")
             return None, True
        return data, True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar odds para o evento {event_id}: {e}")
        return None, False
    except ValueError:
        print(f"Erro ao decodificar JSON da resposta de odds para o evento {event_id}. Resposta: {response.text}")
        return None, True

def process_odds_data(odds_api_response, event_id_for_log="N/A"):
    processed_odds = []
    if not odds_api_response:
        return processed_odds

    markets_payload = odds_api_response.get('markets')
    actual_markets_list = []

    if isinstance(markets_payload, dict):
        actual_markets_list = list(markets_payload.values())
    elif isinstance(markets_payload, list):
        actual_markets_list = markets_payload
    elif markets_payload is None:
        return processed_odds
    else:
        print(f"        Formato inesperado para o payload 'markets' do evento {event_id_for_log}: {type(markets_payload)}")
        return processed_odds

    if not actual_markets_list:
        return processed_odds

    for market_data in actual_markets_list:
        if not isinstance(market_data, dict):
            print(f"          Item inesperado na lista de mercados não é um dicionário: {type(market_data)}, valor: {market_data}. Pulando item.")
            continue

        market_name = market_data.get('marketName', 'N/A')
        short_name = market_data.get('marketNameShort', market_name)
        handicap = market_data.get('handicap', None)
        odds_type = market_data.get('oddsType', 'N/A')

        outcomes_payload = market_data.get('outcomes')
        actual_outcomes_list = []

        if isinstance(outcomes_payload, dict):
            actual_outcomes_list = list(outcomes_payload.values())
        elif isinstance(outcomes_payload, list):
            actual_outcomes_list = outcomes_payload
        elif outcomes_payload is None:
            continue
        else:
            print(f"          Payload 'outcomes' para o mercado '{market_name}' (evento {event_id_for_log}) tem formato inesperado: {type(outcomes_payload)}. Pulando outcomes.")
            continue

        if not actual_outcomes_list:
            continue

        for outcome_data in actual_outcomes_list:
            if not isinstance(outcome_data, dict):
                print(f"            Item inesperado na lista de outcomes não é um dicionário: {type(outcome_data)}, valor: {outcome_data}. Pulando item.")
                continue

            outcome_name_val = outcome_data.get('outcomeName', 'N/A')
            bookmakers_data = outcome_data.get('bookmakers', {})
            bet365_data = bookmakers_data.get('bet365', {}) # Assumindo que sempre queremos bet365 aqui
            odds_value = bet365_data.get('price', None)

            processed_odds.append({
                "market": market_name,
                "short": short_name,
                "handicap": handicap,
                "odds_type": odds_type,
                "outcome": outcome_name_val,
                "odds": odds_value
            })
    return processed_odds
# --- Fim das Funções da API de Odds ---


def run_data_pipeline():
    print("Iniciando pipeline de coleta de dados...")
    all_events_data = []
    total_api_requests = 0

    # --- INÍCIO: Carregar estatísticas dos jogadores (UMA ÚNICA VEZ) ---
    # O ano pode ser um parâmetro ou fixo. Usando 2024 como no exemplo.
    player_stats_map, stats_req_count = get_all_player_stats(year="2024")
    total_api_requests += stats_req_count # Adiciona contagem da API de stats
    if not player_stats_map:
        print("Aviso: Não foi possível carregar as estatísticas dos jogadores. Os eventos não serão enriquecidos com elas.")
    else:
        print(f"Estatísticas de {len(player_stats_map)} jogadores carregadas com sucesso.")
    # --- FIM: Carregar estatísticas dos jogadores ---

    # Verifica se as credenciais da API de Odds estão presentes
    if not ODDS_RAPIDAPI_KEY or not ODDS_RAPIDAPI_HOST:
        print("Erro: RAPIDAPI_KEY ou RAPIDAPI_HOST para a API de Odds não foram encontradas no arquivo .env ou nas variáveis de ambiente.")
        print(f"\nTotal de requisições à API feitas (incluindo stats): {total_api_requests}")
        return [], total_api_requests

    tournaments_data, req_made_tournaments = get_tournaments(sport="tennis")
    if req_made_tournaments: total_api_requests += 1
    if not tournaments_data:
        print("Não foi possível buscar torneios ou resposta vazia.")
        print(f"\nTotal de requisições à API feitas (incluindo stats): {total_api_requests}")
        return all_events_data, total_api_requests

    list_of_tournaments_from_api = []
    if isinstance(tournaments_data, dict):
        list_of_tournaments_from_api = list(tournaments_data.values())
        print(f"Resposta de torneios recebida como dicionário, {len(list_of_tournaments_from_api)} torneios extraídos.")
    elif isinstance(tournaments_data, list):
        list_of_tournaments_from_api = tournaments_data
        print(f"Resposta de torneios recebida como lista, {len(list_of_tournaments_from_api)} torneios.")
    else:
        print(f"Formato inesperado para a resposta de torneios após a busca: {type(tournaments_data)}")
        print(tournaments_data)
        print(f"\nTotal de requisições à API feitas (incluindo stats): {total_api_requests}")
        return all_events_data, total_api_requests

    filtered_tournaments = [
        t for t in list_of_tournaments_from_api
        if t.get("tournamentId") and \
           "Singles" in t.get("name", "") and \
           t.get("categoryName", "") == "ATP"
    ]
    print(f"Encontrados {len(filtered_tournaments)} torneios 'ATP Singles' após o filtro inicial.")
    if not filtered_tournaments:
        print("Nenhum torneio 'ATP Singles' encontrado após o filtro inicial.")
        print(f"\nTotal de requisições à API feitas (incluindo stats): {total_api_requests}")
        return all_events_data, total_api_requests

    for i, tournament in enumerate(filtered_tournaments):
        tournament_id = tournament["tournamentId"]
        tournament_name = tournament["name"]
        tournament_category = tournament.get("categoryName", "N/A")
        print(f"\nTorneio encontrado ({i+1}/{len(filtered_tournaments)}): {tournament_name} (ID: {tournament_id}, Categoria: {tournament_category})")

        while True:
            choice = input(f"  Deseja buscar eventos para este torneio '{tournament_name}'? (y/n): ").lower()
            if choice in ['y', 'n', 's', 'nao', 'sim', 'não']:
                break
            print("  Opção inválida. Por favor, digite 'y' ou 'n'.")
        if choice in ['n', 'nao']:
            print(f"  Pulando torneio '{tournament_name}' conforme solicitado.")
            continue

        print(f"  Buscando eventos para o torneio '{tournament_name}'...")
        time.sleep(1)
        events_response_data, req_made_events = get_events(tournament_id)
        if req_made_events: total_api_requests += 1

        if not events_response_data:
            print(f"  Não foi possível buscar eventos para o torneio {tournament_name} ou resposta vazia.")
            continue

        actual_events_list = []
        events_payload = events_response_data.get('events')
        if isinstance(events_payload, dict):
            actual_events_list = list(events_payload.values())
            print(f"  Resposta de eventos para '{tournament_name}' recebida como dicionário, {len(actual_events_list)} eventos extraídos.")
        elif isinstance(events_payload, list):
            actual_events_list = events_payload
            print(f"  Resposta de eventos para '{tournament_name}' recebida como lista, {len(actual_events_list)} eventos.")
        else:
            print(f"  Formato inesperado para o payload 'events' do torneio {tournament_name}: {type(events_payload)}")
            print(f"  Conteúdo do payload 'events': {events_payload}")
            continue

        if not actual_events_list:
            print(f"  Nenhum evento encontrado no payload para o torneio {tournament_name}.")
            continue
        print(f"  Encontrados {len(actual_events_list)} eventos brutos para o torneio {tournament_name}.")

        processed_event_count_for_tournament = 0
        for j, event_item in enumerate(actual_events_list):
            if not isinstance(event_item, dict):
                print(f"    Item inesperado na lista de eventos não é um dicionário: {type(event_item)}, valor: {event_item}. Pulando item.")
                continue
            event_status = event_item.get("eventStatus")
            if event_status != "pre-game":
                continue
            event_id = event_item.get("eventId")
            if not event_id:
                print(f"    Evento sem ID encontrado no torneio {tournament_name} (após filtro de status). Pulando.")
                continue

            processed_event_count_for_tournament += 1
            participant1_name = event_item.get('participant1', 'N/A')
            participant2_name = event_item.get('participant2', 'N/A')
            print(f"    Processando evento ({processed_event_count_for_tournament}º pré-jogo): {participant1_name} vs {participant2_name} (ID: {event_id}, Status: {event_status})")

            # --- INÍCIO: Buscar estatísticas para os participantes (do mapa em memória) ---
            p1_stats = None
            p2_stats = None
            if player_stats_map: # Só tenta buscar se o mapa de estatísticas foi carregado
                norm_p1_name = normalize_player_name(participant1_name)
                norm_p2_name = normalize_player_name(participant2_name)

                p1_stats = player_stats_map.get(norm_p1_name)
                p2_stats = player_stats_map.get(norm_p2_name)

                if not p1_stats:
                    print(f"      Aviso: Estatísticas não encontradas para {participant1_name} (normalizado como: '{norm_p1_name}')")
                if not p2_stats:
                    print(f"      Aviso: Estatísticas não encontradas para {participant2_name} (normalizado como: '{norm_p2_name}')")
            # --- FIM: Buscar estatísticas para os participantes ---

            time.sleep(0.5)

            odds_data_raw, req_made_odds = get_odds(event_id, bookmakers="bet365")
            if req_made_odds: total_api_requests += 1

            event_odds_processed = process_odds_data(odds_data_raw, event_id)

            if not event_odds_processed:
                print(f"      Nenhuma odd da Bet365 encontrada ou processada para o evento {event_id}.")
            else:
                print(f"      Encontradas {len(event_odds_processed)} linhas de odds da Bet365 para o evento {event_id}.")

            event_info = {
                "tournament_id": tournament_id,
                "tournament_name": tournament_name,
                "tournament_category": tournament_category,
                "event_id": event_id,
                "event_status": event_status,
                "event_date": event_item.get("date"),
                "event_time": event_item.get("time"),
                "participant1": {
                    "name_api": participant1_name, # Nome como veio da API de odds
                    "id_api": event_item.get("participant1Id"),
                    "stats": p1_stats if p1_stats else "N/A" # Adiciona estatísticas ou "N/A"
                },
                "participant2": {
                    "name_api": participant2_name, # Nome como veio da API de odds
                    "id_api": event_item.get("participant2Id"),
                    "stats": p2_stats if p2_stats else "N/A" # Adiciona estatísticas ou "N/A"
                },
                "bookmaker_count_event": event_item.get("bookmakerCount"), # Do evento
                "start_time_unix_event": event_item.get("startTime"), # Do evento
                "odds_bet365": event_odds_processed
            }
            all_events_data.append(event_info)

        if processed_event_count_for_tournament == 0 and actual_events_list:
            print(f"  Nenhum evento 'pre-game' encontrado para o torneio {tournament_name} dentre os {len(actual_events_list)} eventos brutos.")

    print("\nPipeline de coleta de dados concluído.")
    print(f"Total de requisições à API (Odds + Estatísticas): {total_api_requests}")
    return all_events_data, total_api_requests

if __name__ == "__main__":
    collected_data, total_requests = run_data_pipeline()

    print(f"\n--- Resumo da Execução ---")
    print(f"Total de requisições à API: {total_requests}")

    if collected_data:
        print(f"Total de eventos ATP Singles 'pre-game' coletados com suas odds e estatísticas: {len(collected_data)}")
        if collected_data: # Verifica novamente se há dados antes de tentar acessar o índice 0
            print("\nExemplo do primeiro evento ATP Singles 'pre-game' coletado:")
            try:
                print(json.dumps(collected_data[0], indent=2, ensure_ascii=False))
            except IndexError:
                print("Nenhum evento coletado para exibir como exemplo.")

            try:
                with open("dados/collected_tennis_data_atp_singles_pregame_with_stats.json", "w", encoding="utf-8") as f:
                    json.dump(collected_data, f, indent=2, ensure_ascii=False)
                print("\nDados salvos em collected_tennis_data_atp_singles_pregame_with_stats.json")
            except IOError as e:
                print(f"Erro ao salvar o arquivo JSON: {e}")
    else:
        print("Nenhum dado foi coletado (verifique os filtros, confirmações e a disponibilidade nas APIs).")