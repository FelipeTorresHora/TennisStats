# odds.py
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
ODDS_RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
ODDS_RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Headers base para a API de Odds
# É importante que estes sejam para a API de Odds
# Verifique se as variáveis foram carregadas antes de criar os headers
if ODDS_RAPIDAPI_KEY and ODDS_RAPIDAPI_HOST:
    BASE_HEADERS_ODDS = {
        "x-rapidapi-key": ODDS_RAPIDAPI_KEY,
        "x-rapidapi-host": ODDS_RAPIDAPI_HOST
    }
else:
    BASE_HEADERS_ODDS = None # Será verificado depois

# --- Funções da API de Odds ---

def get_tournaments(sport="tennis", headers=None):
    if not headers:
        print("Erro: Headers da API de Odds não configurados para get_tournaments.")
        return None, False
    url = f"https://{headers['x-rapidapi-host']}/tournaments"
    querystring = {"sport": sport}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar torneios: {e}")
        return None, False
    except ValueError: # Erro ao decodificar JSON
        print(f"Erro ao decodificar JSON da resposta de torneios. Resposta: {response.text if 'response' in locals() else 'N/A'}")
        return None, False

def get_events(tournament_id, headers=None, media="false"):
    if not headers:
        print(f"Erro: Headers da API de Odds não configurados para get_events (torneio {tournament_id}).")
        return None, False
    url = f"https://{headers['x-rapidapi-host']}/events"
    querystring = {"tournamentId": tournament_id, "media": media}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar eventos para o torneio {tournament_id}: {e}")
        return None, False
    except ValueError: # Erro ao decodificar JSON
        print(f"Erro ao decodificar JSON da resposta de eventos (torneio {tournament_id}). Resposta: {response.text if 'response' in locals() else 'N/A'}")
        return None, False

def get_odds(event_id, headers=None, bookmakers="bet365", odds_format="decimal", raw="false"):
    if not headers:
        print(f"Erro: Headers da API de Odds não configurados para get_odds (evento {event_id}).")
        return None, False
    url = f"https://{headers['x-rapidapi-host']}/odds"
    querystring = {
        "eventId": event_id,
        "bookmakers": bookmakers,
        "oddsFormat": odds_format,
        "raw": raw
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'markets' not in data and data.get('message'):
            print(f"      Mensagem da API de odds para o evento {event_id} (bookmaker: {bookmakers}): {data['message']}")
            return None, True # Requisição bem-sucedida, mas sem dados de mercado
        elif isinstance(data, list) and not data:
             print(f"      API de odds retornou uma lista vazia para o evento {event_id} (bookmaker: {bookmakers}).")
             return None, True # Requisição bem-sucedida, mas sem dados
        return data, True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar odds para o evento {event_id}: {e}")
        return None, False # Falha na requisição
    except ValueError: # Erro ao decodificar JSON
        print(f"Erro ao decodificar JSON da resposta de odds (evento {event_id}). Resposta: {response.text if 'response' in locals() else 'N/A'}")
        return None, True # Requisição feita, mas JSON inválido

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
            bet365_data = bookmakers_data.get('bet365', {})
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
    player_stats_map, stats_req_count = get_all_player_stats(year="2024") # Assumindo ano fixo
    total_api_requests += stats_req_count
    if not player_stats_map:
        print("Aviso: Não foi possível carregar as estatísticas dos jogadores. Os eventos não serão enriquecidos com elas.")
    else:
        print(f"Estatísticas de {len(player_stats_map)} jogadores carregadas com sucesso.")
    # --- FIM: Carregar estatísticas dos jogadores ---

    # Verifica se as credenciais da API de Odds estão presentes
    if not BASE_HEADERS_ODDS:
        print("Erro Crítico: RAPIDAPI_KEY ou RAPIDAPI_HOST para a API de Odds não foram encontradas no arquivo .env.")
        print("Por favor, configure-as corretamente no arquivo .env.")
        print(f"\nTotal de requisições à API feitas (incluindo stats, se houver): {total_api_requests}")
        return [], total_api_requests

    tournaments_data, req_made_tournaments = get_tournaments(sport="tennis", headers=BASE_HEADERS_ODDS)
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
        events_response_data, req_made_events = get_events(tournament_id, headers=BASE_HEADERS_ODDS)
        if req_made_events: total_api_requests += 1

        if not events_response_data:
            print(f"  Não foi possível buscar eventos para o torneio {tournament_name} ou resposta vazia.")
            continue

        actual_events_list_raw = []
        events_payload = events_response_data.get('events')
        if isinstance(events_payload, dict):
            actual_events_list_raw = list(events_payload.values())
            print(f"  Resposta de eventos para '{tournament_name}' recebida como dicionário, {len(actual_events_list_raw)} eventos extraídos.")
        elif isinstance(events_payload, list):
            actual_events_list_raw = events_payload
            print(f"  Resposta de eventos para '{tournament_name}' recebida como lista, {len(actual_events_list_raw)} eventos.")
        else:
            print(f"  Formato inesperado para o payload 'events' do torneio {tournament_name}: {type(events_payload)}")
            print(f"  Conteúdo do payload 'events': {events_payload}")
            continue

        if not actual_events_list_raw:
            print(f"  Nenhum evento encontrado no payload para o torneio {tournament_name}.")
            continue

        pre_game_events = []
        for event_item_raw in actual_events_list_raw:
            if not isinstance(event_item_raw, dict):
                continue
            if event_item_raw.get("eventStatus") == "pre-game":
                pre_game_events.append(event_item_raw)

        print(f"  Encontrados {len(pre_game_events)} eventos 'pre-game' para o torneio {tournament_name}.")

        if not pre_game_events:
            print(f"  Nenhum evento 'pre-game' encontrado para o torneio {tournament_name}.")
            continue

        processed_event_count_for_tournament_total = 0
        batch_size = 5
        start_index = 0

        while start_index < len(pre_game_events):
            end_index = min(start_index + batch_size, len(pre_game_events))
            current_batch_events = pre_game_events[start_index:end_index]

            print(f"\n    Processando lote de {len(current_batch_events)} eventos 'pre-game' (de {start_index + 1} a {end_index} de {len(pre_game_events)})...")

            for event_item in current_batch_events:
                event_id = event_item.get("eventId")
                if not event_id:
                    print(f"      Evento sem ID encontrado no lote. Pulando.")
                    continue

                processed_event_count_for_tournament_total += 1
                participant1_name = event_item.get('participant1', 'N/A')
                participant2_name = event_item.get('participant2', 'N/A')
                print(f"      Processando evento ({processed_event_count_for_tournament_total}º pré-jogo do torneio): {participant1_name} vs {participant2_name} (ID: {event_id})")

                p1_stats, p2_stats = None, None
                if player_stats_map:
                    norm_p1_name = normalize_player_name(participant1_name)
                    norm_p2_name = normalize_player_name(participant2_name)
                    p1_stats = player_stats_map.get(norm_p1_name)
                    p2_stats = player_stats_map.get(norm_p2_name)
                    if not p1_stats: print(f"        Aviso: Estatísticas não encontradas para {participant1_name} (normalizado: '{norm_p1_name}')")
                    if not p2_stats: print(f"        Aviso: Estatísticas não encontradas para {participant2_name} (normalizado: '{norm_p2_name}')")

                time.sleep(0.5)

                odds_data_raw, req_made_odds = get_odds(event_id, headers=BASE_HEADERS_ODDS, bookmakers="bet365")
                if req_made_odds: total_api_requests += 1

                event_odds_processed = process_odds_data(odds_data_raw, event_id)

                if not event_odds_processed:
                    print(f"        Nenhuma odd da Bet365 encontrada ou processada para o evento {event_id}.")
                else:
                    print(f"        Encontradas {len(event_odds_processed)} linhas de odds da Bet365 para o evento {event_id}.")

                event_info = {
                    "tournament_id": tournament_id,
                    "tournament_name": tournament_name,
                    "tournament_category": tournament_category,
                    "event_id": event_id,
                    "event_status": event_item.get("eventStatus"),
                    "event_date": event_item.get("date"),
                    "event_time": event_item.get("time"),
                    "participant1": {
                        "name_api": participant1_name,
                        "id_api": event_item.get("participant1Id"),
                        "stats": p1_stats if p1_stats else "N/A"
                    },
                    "participant2": {
                        "name_api": participant2_name,
                        "id_api": event_item.get("participant2Id"),
                        "stats": p2_stats if p2_stats else "N/A"
                    },
                    "bookmaker_count_event": event_item.get("bookmakerCount"),
                    "start_time_unix_event": event_item.get("startTime"),
                    "odds_bet365": event_odds_processed
                }
                all_events_data.append(event_info)

            start_index += batch_size

            if start_index < len(pre_game_events):
                while True:
                    remaining_in_tournament = len(pre_game_events) - start_index
                    next_batch_size = min(batch_size, remaining_in_tournament)
                    continue_choice = input(f"    Processados {end_index} de {len(pre_game_events)} eventos 'pre-game' para '{tournament_name}'. Deseja processar os próximos {next_batch_size}? (y/n): ").lower()
                    if continue_choice in ['y', 'n', 's', 'nao', 'sim', 'não']:
                        break
                    print("    Opção inválida. Por favor, digite 'y' ou 'n'.")
                if continue_choice in ['n', 'nao']:
                    print(f"    Interrompendo processamento de eventos para o torneio '{tournament_name}' conforme solicitado.")
                    break
            else:
                print(f"    Todos os {len(pre_game_events)} eventos 'pre-game' para '{tournament_name}' foram processados.")

        if processed_event_count_for_tournament_total == 0 and len(actual_events_list_raw) > 0:
            if start_index >= len(pre_game_events):
                if not any(e.get("eventStatus") == "pre-game" for e in actual_events_list_raw):
                     print(f"  Nenhum evento 'pre-game' encontrado para o torneio {tournament_name} dentre os {len(actual_events_list_raw)} eventos brutos.")

    print("\nPipeline de coleta de dados concluído.")
    print(f"Total de requisições à API (Odds + Estatísticas): {total_api_requests}")
    return all_events_data, total_api_requests

if __name__ == "__main__":
    collected_data, total_requests_made = run_data_pipeline() # Renomeado para evitar conflito

    print(f"\n--- Resumo da Execução ---")
    print(f"Total de requisições à API: {total_requests_made}")

    if collected_data:
        print(f"Total de eventos ATP Singles 'pre-game' coletados com suas odds e estatísticas: {len(collected_data)}")
        if collected_data:
            print("\nExemplo do primeiro evento ATP Singles 'pre-game' coletado (se houver):")
            try:
                print(json.dumps(collected_data[0], indent=2, ensure_ascii=False))
            except IndexError:
                print("Nenhum evento coletado para exibir como exemplo.")

            try:
                output_filename = "collected_tennis_data_atp_singles_pregame_with_stats.json"
                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(collected_data, f, indent=2, ensure_ascii=False)
                print(f"\nDados salvos em {output_filename}")
            except IOError as e:
                print(f"Erro ao salvar o arquivo JSON: {e}")
    else:
        print("Nenhum dado foi coletado (verifique os filtros, confirmações e a disponibilidade nas APIs).")