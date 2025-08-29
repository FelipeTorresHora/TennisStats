import requests
import json
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
TOURNAMENT_ID = "20340"  # ID do último torneio

def get_tournament_results():
    """
    Busca todos os resultados do torneio para extrair IDs dos jogadores
    """
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/atp/tournament/results/{TOURNAMENT_ID}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }
    
    try:
        print(f"🔍 Buscando resultados do torneio ID: {TOURNAMENT_ID}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Dados do torneio coletados com sucesso")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição do torneio: {e}")
        return None
    except ValueError as e:
        print(f"❌ Erro ao decodificar JSON do torneio: {e}")
        return None

def extract_player_ids_from_tournament(tournament_data):
    """
    Extrai todos os IDs únicos de jogadores do torneio
    """
    player_ids = set()
    players_info = {}
    
    def extract_from_matches(matches_data):
        if isinstance(matches_data, list):
            for match in matches_data:
                if isinstance(match, dict):
                    # Extrair jogadores do match
                    for key in ['homeTeam', 'awayTeam', 'participant1', 'participant2']:
                        if key in match:
                            player_data = match[key]
                            if isinstance(player_data, dict):
                                player_id = player_data.get('id')
                                player_name = player_data.get('name')
                                if player_id:
                                    player_ids.add(str(player_id))
                                    players_info[str(player_id)] = {
                                        'id': player_id,
                                        'name': player_name,
                                        'found_in': 'tournament_results'
                                    }
    
    def recursive_search(data, path=""):
        """Busca recursivamente por dados de jogadores em toda a estrutura"""
        if isinstance(data, dict):
            # Verificar se é um objeto de jogador
            if 'id' in data and 'name' in data:
                player_id = data.get('id')
                player_name = data.get('name')
                if player_id and player_name:
                    player_ids.add(str(player_id))
                    players_info[str(player_id)] = {
                        'id': player_id,
                        'name': player_name,
                        'found_in': path or 'tournament_data'
                    }
            
            # Continuar busca recursiva
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                if key in ['matches', 'results', 'rounds', 'participants']:
                    extract_from_matches(value)
                recursive_search(value, new_path)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                recursive_search(item, new_path)
    
    # Buscar em toda a estrutura do torneio
    recursive_search(tournament_data)
    
    print(f"🎾 Encontrados {len(player_ids)} jogadores únicos no torneio")
    return list(player_ids), players_info

def filter_players_from_stats_csv(tournament_player_ids, players_info):
    """
    Filtra jogadores que estão tanto no torneio quanto no stats.csv
    """
    # Verificar se o arquivo stats.csv existe
    if not os.path.exists('stats.csv'):
        print("⚠️ Arquivo stats.csv não encontrado! Usando todos os jogadores do torneio.")
        return tournament_player_ids, players_info
    
    try:
        df_stats = pd.read_csv('stats.csv')
        print(f"📊 Arquivo stats.csv carregado com {len(df_stats)} jogadores")
        
        # Verificar se tem coluna NomeJogador para fazer matching por nome
        if 'NomeJogador' in df_stats.columns:
            stats_names = set(df_stats['NomeJogador'].dropna().str.lower().str.strip())
            
            filtered_players = []
            filtered_info = {}
            
            for player_id in tournament_player_ids:
                player_info = players_info.get(player_id, {})
                player_name = player_info.get('name', '').lower().strip()
                
                if player_name in stats_names:
                    filtered_players.append(player_id)
                    filtered_info[player_id] = player_info
                    print(f"  ✅ Match encontrado: {player_info.get('name')} (ID: {player_id})")
            
            print(f"🎯 Filtro aplicado: {len(filtered_players)} jogadores do torneio estão no stats.csv")
            return filtered_players, filtered_info
        else:
            print("⚠️ Coluna 'NomeJogador' não encontrada no stats.csv. Usando todos os jogadores do torneio.")
            return tournament_player_ids, players_info
            
    except Exception as e:
        print(f"❌ Erro ao ler stats.csv: {e}")
        print("Usando todos os jogadores do torneio.")
        return tournament_player_ids, players_info

def get_player_surface_summary(player_id):
    """
    Busca o resumo completo por superfície de um jogador
    """
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/atp/player/surface-summary/{player_id}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro surface-summary para jogador {player_id}: {e}")
        return None
    except ValueError as e:
        print(f"  ❌ Erro JSON surface-summary para jogador {player_id}: {e}")
        return None

def get_player_past_matches(player_id):
    """
    Busca TODOS os jogos passados de um jogador
    """
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/atp/player/past-matches/{player_id}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro past-matches para jogador {player_id}: {e}")
        return None
    except ValueError as e:
        print(f"  ❌ Erro JSON past-matches para jogador {player_id}: {e}")
        return None

def collect_tournament_players_data():
    """
    Função principal que coleta dados de todos os jogadores do torneio
    """
    # Buscar dados do torneio
    tournament_data = get_tournament_results()
    if not tournament_data:
        print("❌ Não foi possível obter dados do torneio")
        return
    
    # Extrair IDs dos jogadores
    tournament_player_ids, players_info = extract_player_ids_from_tournament(tournament_data)
    if not tournament_player_ids:
        print("❌ Nenhum jogador encontrado no torneio")
        return
    
    # Filtrar jogadores que estão no stats.csv
    filtered_player_ids, filtered_players_info = filter_players_from_stats_csv(tournament_player_ids, players_info)
    
    if not filtered_player_ids:
        print("❌ Nenhum jogador do torneio encontrado no stats.csv")
        return
    
    # Dicionário para armazenar todos os dados
    all_players_data = {
        'tournament_info': {
            'tournament_id': TOURNAMENT_ID,
            'collected_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_players_in_tournament': len(tournament_player_ids),
            'filtered_players_count': len(filtered_player_ids),
            'tournament_raw_data': tournament_data
        },
        'players': {}
    }
    
    consecutive_failures = 0
    total_processed = 0
    total_success = 0
    
    print(f"\\n🚀 Iniciando coleta detalhada para {len(filtered_player_ids)} jogadores filtrados...")
    
    for player_id in filtered_player_ids:
        player_info = filtered_players_info.get(player_id, {})
        player_name = player_info.get('name', f'Player_{player_id}')
        
        print(f"\\n📊 Coletando: {player_name} (ID: {player_id})")
        total_processed += 1
        
        # Estrutura base do jogador
        player_data = {
            'player_info': player_info,
            'collected_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'surface_summary': None,
            'past_matches': None
        }
        
        # Buscar surface summary
        print(f"  🔍 Buscando surface summary...")
        surface_summary = get_player_surface_summary(player_id)
        if surface_summary:
            player_data['surface_summary'] = surface_summary
            print(f"  ✅ Surface summary coletado")
        else:
            print(f"  ⚠️ Surface summary não disponível")
        
        # Buscar past matches
        print(f"  🔍 Buscando past matches...")
        past_matches = get_player_past_matches(player_id)
        if past_matches:
            player_data['past_matches'] = past_matches
            # Contar matches
            matches_count = 0
            if isinstance(past_matches, dict) and 'data' in past_matches:
                matches_data = past_matches['data']
                if isinstance(matches_data, dict) and 'matches' in matches_data:
                    matches_count = len(matches_data['matches'])
            print(f"  ✅ Past matches coletado ({matches_count} jogos)")
        else:
            print(f"  ⚠️ Past matches não disponível")
        
        # Verificar se pelo menos um endpoint retornou dados
        if surface_summary is None and past_matches is None:
            consecutive_failures += 1
            print(f"  ❌ Falha consecutiva #{consecutive_failures} para {player_name}")
            
            if consecutive_failures >= 5:
                print(f"\\n🛑 ERRO: 5 falhas consecutivas detectadas!")
                print(f"Parando execução - possível problema no código ou API")
                break
            continue
        
        # Reset contador de falhas
        consecutive_failures = 0
        total_success += 1
        
        # Armazenar dados do jogador
        player_key = f"{player_name}_{player_id}".replace(" ", "_")
        all_players_data['players'][player_key] = player_data
        
        print(f"  ✅ Dados completos coletados para {player_name}")
        
        # Delay para evitar rate limiting
        time.sleep(1)
    
    # Salvar os dados em JSON
    if all_players_data['players']:
        output_filename = 'dados/raw/stats3_raw.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_players_data, f, indent=2, ensure_ascii=False)
        
        print(f"\\n Arquivo {output_filename} criado com sucesso!")
        print(f" Estatísticas da coleta:")
        print(f"  • Torneio ID: {TOURNAMENT_ID}")
        print(f"  • Jogadores no torneio: {all_players_data['tournament_info']['total_players_in_tournament']}")
        print(f"  • Jogadores filtrados: {len(filtered_player_ids)}")
        print(f"  • Total processados: {total_processed}")
        print(f"  • Total sucessos: {total_success}")
        print(f"  • Jogadores no JSON: {len(all_players_data['players'])}")
        
    else:
        print(f"\\n Nenhum dado foi coletado com sucesso!")

if __name__ == "__main__":
        collect_tournament_players_data()
        print("\\n🏁 Coleta finalizada!")
