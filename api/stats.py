import requests
import json
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

STATS_RAPIDAPI_KEY = os.getenv("STATS_RAPIDAPI_KEY", os.getenv("RAPIDAPI_KEY"))

def get_player_stats_ultimate_tennis(player_id, season="2024", surface="clay"):
    """
    Busca todos os dados de um jogador na Ultimate Tennis API
    """
    url = f"https://ultimate-tennis1.p.rapidapi.com/player_stats/atp/{player_id}/{season}/{surface}"
    headers = {
        "x-rapidapi-key": STATS_RAPIDAPI_KEY,
        "x-rapidapi-host": "ultimate-tennis1.p.rapidapi.com"
    }
    
    try:
        print(f"🔍 Buscando dados para jogador ID: {player_id}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Retorna a resposta completa da API
        if data:
            print(f"  ✅ Dados coletados para jogador {player_id}")
            return data
        else:
            print(f"  ⚠️ Resposta vazia para jogador {player_id}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro na requisição para jogador {player_id}: {e}")
        return None
    except ValueError as e:
        print(f"  ❌ Erro ao decodificar JSON para jogador {player_id}: {e}")
        return None

def collect_all_players_data():
    """
    Coleta dados de todos os jogadores do stats.csv e salva em JSON
    """
    # Verificar se o arquivo stats.csv existe
    if not os.path.exists('dados/stats.csv'):
        print("❌ Erro: Arquivo stats.csv não encontrado!")
        return
    
    # Ler o arquivo stats.csv
    try:
        df_original = pd.read_csv('dados/stats.csv')
        print(f"📊 Arquivo stats.csv carregado com {len(df_original)} jogadores")
    except Exception as e:
        print(f"❌ Erro ao ler stats.csv: {e}")
        return
    
    # Verificar se a coluna IdJogador existe
    if 'IdJogador' not in df_original.columns:
        print("❌ Erro: Coluna 'IdJogador' não encontrada no stats.csv!")
        return
    
    # Dicionário para armazenar os dados (chave = ID do jogador)
    all_players_data = {}
    consecutive_failures = 0
    total_processed = 0
    total_success = 0
    
    print(f"\\n🚀 Iniciando coleta de dados para {len(df_original)} jogadores...")
    
    # Processar cada jogador
    for index, row in df_original.iterrows():
        player_id = row['IdJogador']
        
        if pd.isna(player_id):
            print(f"⚠️ ID do jogador na linha {index} está vazio, pulando...")
            continue
        
        total_processed += 1
        
        # Buscar dados na API
        player_data = get_player_stats_ultimate_tennis(player_id)
        
        if player_data is None:
            consecutive_failures += 1
            print(f"  ❌ Falha consecutiva #{consecutive_failures} para jogador {player_id}")
            
            # Verificar se atingiu 5 falhas consecutivas
            if consecutive_failures >= 5:
                print(f"\\n🛑 ERRO: 5 falhas consecutivas detectadas!")
                print(f"Parando execução - possível problema no código ou API")
                print(f"Último jogador que falhou: {player_id}")
                break
            
            continue
        
        # Reset contador de falhas consecutivas se teve sucesso
        consecutive_failures = 0
        total_success += 1
        
        # Armazenar dados completos com ID como chave
        all_players_data[str(player_id)] = {
            'player_id': player_id,
            'collected_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'api_response': player_data
        }
        
        # Pequeno delay para evitar rate limiting
        time.sleep(0.5)
    
    # Salvar os dados em JSON
    if all_players_data:
        output_filename = 'dados/raw/stats_raw.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_players_data, f, indent=2, ensure_ascii=False)
        
        print(f"\\n Arquivo {output_filename} criado com sucesso!")
        print(f" Estatísticas da coleta:")
        print(f"  • Total processados: {total_processed}")
        print(f"  • Total sucessos: {total_success}")
        print(f"  • Total falhas: {total_processed - total_success}")
        print(f"  • Jogadores no JSON: {len(all_players_data)}")
        
        # Mostrar exemplo de um jogador
        if all_players_data:
            first_key = next(iter(all_players_data))
            first_player = all_players_data[first_key]
            print(f"\\n📋 Exemplo de estrutura (Jogador ID: {first_key}):")
            print(f"  • Coletado em: {first_player['collected_at']}")
            print(f"  • Campos na resposta da API: {len(first_player['api_response']) if isinstance(first_player['api_response'], dict) else 'N/A'}")
            
    else:
        print(f"\\n❌ Nenhum dado foi coletado com sucesso!")

if __name__ == "__main__":
        collect_all_players_data()
        print("\\n🏁 Coleta finalizada!")