import requests
import json
import os
import time
from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def get_top50_rankings():
    """
    Busca o ranking completo dos top 50 jogadores ATP
    """
    url = "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/atp/ranking/singles/"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }
    
    try:
        print("🔍 Buscando ranking dos top 50 jogadores ATP...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extrair os top 50 jogadores
        ranking_data = data.get('data', [])
        top50_players = ranking_data[:150]  # Limitar aos top 50
        
        print(f"✅ {len(top50_players)} jogadores do ranking coletados")
        return top50_players
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição de ranking: {e}")
        return []
    except ValueError as e:
        print(f"❌ Erro ao decodificar JSON do ranking: {e}")
        return []

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
        return data  # Retorna resposta completa da API
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro surface-summary para jogador {player_id}: {e}")
        return None
    except ValueError as e:
        print(f"  ❌ Erro JSON surface-summary para jogador {player_id}: {e}")
        return None

def get_player_past_matches(player_id):
    """
    Busca TODOS os jogos passados de um jogador (sem limite)
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
        return data  # Retorna resposta completa da API
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro past-matches para jogador {player_id}: {e}")
        return None
    except ValueError as e:
        print(f"  ❌ Erro JSON past-matches para jogador {player_id}: {e}")
        return None

def collect_all_top50_data():
    """
    Coleta dados completos de todos os top 50 jogadores e salva em JSON
    """
    # Buscar ranking dos top 50
    top50_players = get_top50_rankings()
    
    if not top50_players:
        print("❌ Não foi possível obter o ranking dos top 50")
        return
    
    # Dicionário para armazenar todos os dados organizados por jogador
    all_players_data = {}
    consecutive_failures = 0
    total_processed = 0
    total_success = 0
    
    print(f"\\n🚀 Iniciando coleta completa para {len(top50_players)} jogadores...")
    
    for player_entry in top50_players:
        player_info = player_entry.get('player', {})
        player_id = player_info.get('id')
        player_name = player_info.get('name')
        
        if not player_id or not player_name:
            print(f"⚠️ Dados incompletos para jogador: {player_entry}")
            continue
        
        print(f"\\n📊 Coletando: {player_name} (ID: {player_id})")
        total_processed += 1
        
        # Estrutura base do jogador
        player_data = {
            'player_info': {
                'id': player_id,
                'name': player_name,
                'ranking_data': player_entry  # Dados completos do ranking
            },
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
        
        # Buscar past matches (TODOS os dados)
        print(f"  🔍 Buscando past matches...")
        past_matches = get_player_past_matches(player_id)
        if past_matches:
            player_data['past_matches'] = past_matches
            # Contar quantos matches foram coletados
            matches_count = 0
            if isinstance(past_matches, dict) and 'data' in past_matches:
                matches_data = past_matches['data']
                if isinstance(matches_data, dict) and 'matches' in matches_data:
                    matches_count = len(matches_data['matches'])
                elif isinstance(matches_data, list):
                    matches_count = len(matches_data)
            print(f"  ✅ Past matches coletado ({matches_count} jogos)")
        else:
            print(f"  ⚠️ Past matches não disponível")
        
        # Verificar se pelo menos um endpoint retornou dados
        if surface_summary is None and past_matches is None:
            consecutive_failures += 1
            print(f"  ❌ Falha consecutiva #{consecutive_failures} para {player_name}")
            
            # Verificar se atingiu 5 falhas consecutivas
            if consecutive_failures >= 5:
                print(f"\\n🛑 ERRO: 5 falhas consecutivas detectadas!")
                print(f"Parando execução - possível problema no código ou API")
                print(f"Último jogador que falhou: {player_name} (ID: {player_id})")
                break
            
            continue
        
        # Reset contador de falhas consecutivas se teve sucesso
        consecutive_failures = 0
        total_success += 1
        
        # Armazenar dados do jogador (usando nome como chave para facilitar)
        player_key = f"{player_name}_{player_id}"
        all_players_data[player_key] = player_data
        
        print(f"  ✅ Dados completos coletados para {player_name}")
        
        # Delay para evitar rate limiting
        time.sleep(1)
    
    # Salvar os dados em JSON
    if all_players_data:
        output_filename = 'dados/raw/stats2_raw.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_players_data, f, indent=2, ensure_ascii=False)
        
        print(f"\\n✅ Arquivo {output_filename} criado com sucesso!")
        print(f"📈 Estatísticas da coleta:")
        print(f"  • Total processados: {total_processed}")
        print(f"  • Total sucessos: {total_success}")
        print(f"  • Total falhas: {total_processed - total_success}")
        print(f"  • Jogadores no JSON: {len(all_players_data)}")
            
    else:
        print(f"\\n Nenhum dado foi coletado com sucesso!")

if __name__ == "__main__":
        collect_all_top50_data()
        print("\\n🏁 Coleta finalizada!")
