import requests
import time
import json
import os
from dotenv import load_dotenv # Importe load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

# Acesse as variáveis de ambiente
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

BASE_HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

def get_tournaments(sport="tennis"):
    url = f"https://{RAPIDAPI_HOST}/tournaments"
    querystring = {"sport": sport}
    try:
        response = requests.get(url, headers=BASE_HEADERS, params=querystring)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar torneios: {e}")
        return None, False
    except ValueError:
        print(f"Erro ao decodificar JSON da resposta de torneios. Resposta: {response.text}")
        return None, False

def get_events(tournament_id, media="false"):
    url = f"https://{RAPIDAPI_HOST}/events"
    querystring = {"tournamentId": tournament_id, "media": media}
    try:
        response = requests.get(url, headers=BASE_HEADERS, params=querystring)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar eventos para o torneio {tournament_id}: {e}")
        return None, False
    except ValueError:
        print(f"Erro ao decodificar JSON da resposta de eventos. Resposta: {response.text}")
        return None, False

def get_odds(event_id, bookmakers="bet365", odds_format="decimal", raw="false"):
    url = f"https://{RAPIDAPI_HOST}/odds"
    querystring = {
        "eventId": event_id,
        "bookmakers": bookmakers,
        "oddsFormat": odds_format,
        "raw": raw
    }
    try:
        response = requests.get(url, headers=BASE_HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()
        # Verifica se a resposta é um dicionário e se a chave 'markets' está ausente,
        # mas existe uma chave 'message' (indicando uma mensagem da API como "odds não disponíveis")
        if isinstance(data, dict) and 'markets' not in data and data.get('message'):
            print(f"      Mensagem da API de odds para o evento {event_id} (bookmaker: {bookmakers}): {data['message']}")
            return None, True # Requisição bem-sucedida, mas sem dados de mercado
        # Verifica se a resposta é uma lista vazia
        elif isinstance(data, list) and not data:
             print(f"      API de odds retornou uma lista vazia para o evento {event_id} (bookmaker: {bookmakers}).")
             return None, True # Requisição bem-sucedida, mas sem dados
        return data, True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar odds para o evento {event_id}: {e}")
        return None, False # Falha na requisição
    except ValueError: # Erro ao decodificar JSON
        print(f"Erro ao decodificar JSON da resposta de odds para o evento {event_id}. Resposta: {response.text}")
        return None, True # Requisição feita, mas JSON inválido
    
def process_odds_data(odds_api_response, event_id_for_log="N/A"):
    processed_odds = []
    if not odds_api_response:
        return processed_odds

    # Descomente para depuração da estrutura completa da resposta de odds
    # print(f"DEBUG: process_odds_data: odds_api_response for event {event_id_for_log}: {json.dumps(odds_api_response, indent=2)}")

    markets_payload = odds_api_response.get('markets')
    actual_markets_list = []

    if isinstance(markets_payload, dict):
        actual_markets_list = list(markets_payload.values())
    elif isinstance(markets_payload, list):
        actual_markets_list = markets_payload
    elif markets_payload is None:
        # print(f"        Nenhum payload 'markets' encontrado para o evento {event_id_for_log}.")
        return processed_odds
    else:
        print(f"        Formato inesperado para o payload 'markets' do evento {event_id_for_log}: {type(markets_payload)}")
        return processed_odds

    if not actual_markets_list:
        # print(f"        Nenhum mercado encontrado no payload processado para o evento {event_id_for_log}.")
        return processed_odds

    for market_data in actual_markets_list:
        if not isinstance(market_data, dict):
            print(f"          Item inesperado na lista de mercados não é um dicionário: {type(market_data)}, valor: {market_data}. Pulando item.")
            continue

        market_name = market_data.get('marketName', 'N/A')
        # A API usa marketNameShort para o que chamamos de 'short' no CSV
        short_name = market_data.get('marketNameShort', market_name) # Corrigido para marketNameShort
        handicap = market_data.get('handicap', None)
        odds_type = market_data.get('oddsType', 'N/A')

        outcomes_payload = market_data.get('outcomes')
        actual_outcomes_list = []

        if isinstance(outcomes_payload, dict):
            actual_outcomes_list = list(outcomes_payload.values())
        elif isinstance(outcomes_payload, list):
            actual_outcomes_list = outcomes_payload
        elif outcomes_payload is None:
            # print(f"            Nenhum payload 'outcomes' encontrado para o mercado '{market_name}' (evento {event_id_for_log}).")
            continue
        else:
            print(f"          Payload 'outcomes' para o mercado '{market_name}' (evento {event_id_for_log}) tem formato inesperado: {type(outcomes_payload)}. Pulando outcomes.")
            continue

        if not actual_outcomes_list:
            # print(f"            Nenhum outcome encontrado no payload processado para o mercado '{market_name}' (evento {event_id_for_log}).")
            continue

        for outcome_data in actual_outcomes_list:
            if not isinstance(outcome_data, dict):
                print(f"            Item inesperado na lista de outcomes não é um dicionário: {type(outcome_data)}, valor: {outcome_data}. Pulando item.")
                continue

            # Descomente para depuração da estrutura de cada outcome_data
            # print(f"DEBUG: outcome_data for event {event_id_for_log}, market '{market_name}': {json.dumps(outcome_data, indent=2)}")

            # --- CORREÇÃO PRINCIPAL AQUI ---
            outcome_name_val = outcome_data.get('outcomeName', 'N/A') # Usar 'outcomeName'

            # Navegar para bookmakers -> bet365 -> price
            bookmakers_data = outcome_data.get('bookmakers', {})
            bet365_data = bookmakers_data.get('bet365', {})
            odds_value = bet365_data.get('price', None)
            # --- FIM DA CORREÇÃO PRINCIPAL ---

            processed_odds.append({
                "market": market_name,
                "short": short_name,
                "handicap": handicap,
                "odds_type": odds_type,
                "outcome": outcome_name_val, # Usar o valor corrigido
                "odds": odds_value         # Usar o valor corrigido
            })
    return processed_odds    

def run_data_pipeline():
    print("Iniciando pipeline de coleta de dados...")
    all_events_data = []
    request_count = 0

    tournaments_data, req_made_tournaments = get_tournaments(sport="tennis")
    if req_made_tournaments: request_count += 1
    if not tournaments_data:
        print("Não foi possível buscar torneios ou resposta vazia.")
        print(f"\nTotal de requisições à API feitas: {request_count}")
        return all_events_data, request_count

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
        print(f"\nTotal de requisições à API feitas: {request_count}")
        return all_events_data, request_count

    filtered_tournaments = [
        t for t in list_of_tournaments_from_api
        if t.get("tournamentId") and \
           "Singles" in t.get("name", "") and \
           t.get("categoryName", "") == "ATP"
    ]
    print(f"Encontrados {len(filtered_tournaments)} torneios 'ATP Singles' após o filtro inicial.")
    if not filtered_tournaments:
        print("Nenhum torneio 'ATP Singles' encontrado após o filtro inicial.")
        print(f"\nTotal de requisições à API feitas: {request_count}")
        return all_events_data, request_count

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
        time.sleep(1) # Pequeno delay para não sobrecarregar a API
        events_response_data, req_made_events = get_events(tournament_id)
        if req_made_events: request_count += 1

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
            time.sleep(0.5) # Pequeno delay

            odds_data_raw, req_made_odds = get_odds(event_id, bookmakers="bet365")
            if req_made_odds: request_count += 1

            event_odds_processed = process_odds_data(odds_data_raw, event_id)

            if not event_odds_processed:
                # Mensagens de erro específicas já são logadas em get_odds ou process_odds_data
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
                "participant1": participant1_name,
                "participant1_id": event_item.get("participant1Id"),
                "participant2": participant2_name,
                "participant2_id": event_item.get("participant2Id"),
                "bookmaker_count": event_item.get("bookmakerCount"), # Do evento
                "start_time_unix": event_item.get("startTime"), # Do evento
                "odds_bet365": event_odds_processed
            }
            all_events_data.append(event_info)

        if processed_event_count_for_tournament == 0 and actual_events_list: # Verifica se havia eventos brutos
            print(f"  Nenhum evento 'pre-game' encontrado para o torneio {tournament_name} dentre os {len(actual_events_list)} eventos brutos.")

    print("\nPipeline de coleta de dados concluído.")
    print(f"Total de requisições à API feitas: {request_count}")
    return all_events_data, request_count


if __name__ == "__main__":
    collected_data, total_requests = run_data_pipeline()

    print(f"\n--- Resumo da Execução ---")
    print(f"Total de requisições à API: {total_requests}")

    if collected_data:
        print(f"Total de eventos ATP Singles 'pre-game' coletados com suas odds: {len(collected_data)}")
        if collected_data:
            print("\nExemplo do primeiro evento ATP Singles 'pre-game' coletado:")
            try:
                print(json.dumps(collected_data[0], indent=2, ensure_ascii=False))
            except IndexError:
                print("Nenhum evento coletado para exibir como exemplo.")

            # Salvar os dados coletados em um arquivo JSON
            try:
                with open("collected_tennis_data_atp_singles_pregame.json", "w", encoding="utf-8") as f:
                    json.dump(collected_data, f, indent=2, ensure_ascii=False)
                print("\nDados salvos em collected_tennis_data_atp_singles_pregame.json")
            except IOError as e:
                print(f"Erro ao salvar o arquivo JSON: {e}")
    else:
        print("Nenhum dado foi coletado (verifique os filtros, confirmações e a disponibilidade na API).")