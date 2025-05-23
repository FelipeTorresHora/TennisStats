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