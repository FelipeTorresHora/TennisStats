import json
import pandas as pd
from collections import defaultdict

# Carregar os arquivos
with open('dados/raw/stats_raw.json', 'r', encoding='utf-8') as f:
    stats_raw = json.load(f)

with open('dados/raw/stats2_raw.json', 'r', encoding='utf-8') as f:
    stats2_raw = json.load(f)

stats_csv = pd.read_csv('dados/clean/stats.csv')

# Criar dicionário para mapear player_id -> nome
id_to_name = {}
for _, row in stats_csv.iterrows():
    if pd.notna(row['IdJogador']) and pd.notna(row['NomeJogador']):
        id_to_name[row['IdJogador']] = row['NomeJogador']

# Inicializar stats_clean
stats_clean = {}

# Processar stats_raw.json
for player_id, player_data in stats_raw.items():
    if player_id not in id_to_name:
        continue
    
    player_name = id_to_name[player_id]
    
    # Inicializar dados do jogador
    if player_name not in stats_clean:
        stats_clean[player_name] = {
            "player_id": player_id,
            "name": player_name
        }
    
    # Processar api_response
    if 'api_response' in player_data:
        api_resp = player_data['api_response']
        
        # Verificar se é uma lista de superfícies ou um único objeto
        surfaces_data = api_resp if isinstance(api_resp, list) else [api_resp]
        
        for surface_data in surfaces_data:
            if isinstance(surface_data, dict) and 'Surface' in surface_data:
                surface = surface_data['Surface']
                
                # Adicionar ReturnRecordStats com sufixo da superfície
                if 'ReturnRecordStats' in surface_data:
                    key_name = f"ReturnRecordStats{surface}"
                    stats_clean[player_name][key_name] = surface_data['ReturnRecordStats']
                
                # Adicionar ServiceRecordStats com sufixo da superfície
                if 'ServiceRecordStats' in surface_data:
                    key_name = f"ServiceRecordStats{surface}"
                    stats_clean[player_name][key_name] = surface_data['ServiceRecordStats']

# Função para normalizar nomes
def normalize_name(name):
    return name.lower().replace(' ', '').replace('-', '').replace('.', '')

# Criar mapeamento de nomes normalizados
name_mapping = {}
for name in stats_clean.keys():
    normalized = normalize_name(name)
    name_mapping[normalized] = name

# Processar stats2_raw.json
for player_key, player_data in stats2_raw.items():
    # Extrair nome do jogador (formato: "Nome_ID")
    if '_' in player_key:
        player_name_raw = player_key.split('_')[0].replace('_', ' ').strip()
    else:
        player_name_raw = player_key.strip()
    
    # Tentar encontrar match no stats_clean
    normalized_search = normalize_name(player_name_raw)
    matched_name = None
    
    # Busca exata
    if normalized_search in name_mapping:
        matched_name = name_mapping[normalized_search]
    else:
        # Busca parcial
        for norm_name, real_name in name_mapping.items():
            if normalized_search in norm_name or norm_name in normalized_search:
                matched_name = real_name
                break
    
    if matched_name:
        # Processar surface_summary (apenas 2023+)
        if 'surface_summary' in player_data:
            surface_data = player_data['surface_summary']
            
            if 'data' in surface_data and isinstance(surface_data['data'], list):
                surface_list = surface_data['data']
                
                # Filtrar itens de 2023+
                filtered_items = []
                
                for item in surface_list:
                    if isinstance(item, dict):
                        # Procurar campo de ano
                        year_found = None
                        for key, value in item.items():
                            if key.lower() in ['year', 'season', 'eventyear'] or 'year' in key.lower():
                                try:
                                    year_found = int(value)
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        # Se encontrou ano >= 2023, incluir
                        if year_found and year_found >= 2023:
                            filtered_items.append(item)
                
                if filtered_items:
                    stats_clean[matched_name]['surface_summary'] = filtered_items
        
        # Processar past_matches
        if 'past_matches' in player_data:
            stats_clean[matched_name]['past_matches'] = player_data['past_matches']

# Criar o arquivo stats_clean.json
with open('dados/clean/stats_clean.json', 'w', encoding='utf-8') as f:
    json.dump(stats_clean, f, indent=2, ensure_ascii=False)