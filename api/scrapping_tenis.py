# scrapping_tenis.py
import json
import os
import time
import csv

def normalize_player_name_for_key(name):
    """Normaliza nome para criar chaves consistentes ou para busca."""
    if not name:
        return ""
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 2:
            name = f"{parts[1].strip()} {parts[0].strip()}"
    return name.lower().strip()

def load_player_name_map(file_path='dados/clean/stats.csv'):
    """Carrega o stats.csv para mapear IdJogador para NomeJogador."""
    if not os.path.exists(file_path):
        print(f"Aviso: Arquivo de mapeamento de nomes {file_path} não encontrado.")
        return {}
    
    name_map = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_id = row.get('IdJogador')
                player_name = row.get('NomeJogador')
                if player_id and player_name:
                    name_map[str(player_id)] = player_name
        print(f"Mapeamento de nomes carregado com {len(name_map)} jogadores de {file_path}.")
        return name_map
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        return {}


def find_or_create_player_record(name, player_id, unified_stats, name_to_id_map):
    """
    Encontra um registro de jogador existente pelo nome ou cria um novo.
    Prioriza IDs numéricos como chaves canônicas.
    """
    normalized_name = normalize_player_name_for_key(name)
    if not normalized_name:
        return None, None

    canonical_id = name_to_id_map.get(normalized_name)

    if canonical_id:
        # Jogador já existe, retorna o registro existente
        return unified_stats[canonical_id], canonical_id
    else:
        # Novo jogador, cria um novo registro
        new_id = str(player_id)
        name_to_id_map[normalized_name] = new_id
        
        unified_stats[new_id] = {
            "player_id": new_id, # ID canônico será este por enquanto
            "names": set(),
            "sources": set(),
            "stats": {"surface": {}},
            "past_matches": [],
            "ranking_data": None,
            "alternate_ids": set()
        }
        return unified_stats[new_id], new_id

def process_stats_ultimate_tennis(data, unified_stats, name_to_id_map, player_name_map):
    """Processa dados da Ultimate Tennis API (stats_raw_hard.json, etc.)"""
    print(f"Processando {len(data)} jogadores da Ultimate Tennis API...")
    for player_id_str, player_data in data.items():
        # Usa o mapa de nomes para encontrar o nome do jogador
        player_name = player_name_map.get(player_id_str)
        if not player_name:
            print(f"  Aviso: Nome não encontrado para o ID {player_id_str} no stats.csv. Pulando.")
            continue

        api_response = player_data.get('api_response', {})
        if not api_response:
            continue
            
        # Encontra ou cria o registro do jogador no 'unified_stats'
        player_record, canonical_id = find_or_create_player_record(player_name, player_id_str, unified_stats, name_to_id_map)
        
        if not player_record:
            continue

        # Atualiza os dados do jogador
        player_record["names"].add(player_name)
        player_record["sources"].add("ultimate-tennis")
        if canonical_id != player_id_str:
            player_record["alternate_ids"].add(player_id_str)
        
        # Adiciona estatísticas da superfície (grama, saibro, etc.)
        surface_key = api_response.get('Surface', 'unknown').lower()
        player_record["stats"]["surface"][surface_key] = api_response

def process_stats_tennis_api(data, unified_stats, name_to_id_map):
    """Processa dados da Tennis API (stats2_raw.json, stats3_raw.json)"""
    players_data = data.get('players', {})
    print(f"Processando {len(players_data)} jogadores da Tennis API...")
    
    for player_key, player_full_data in players_data.items():
        player_info = player_full_data.get('player_info', {})
        player_id = str(player_info.get('id'))
        player_name = player_info.get('name')

        if not player_id or not player_name:
            continue
            
        # Encontra ou cria o registro do jogador no 'unified_stats'
        player_record, canonical_id = find_or_create_player_record(player_name, player_id, unified_stats, name_to_id_map)
        
        if not player_record:
            continue

        # Atualiza os dados do jogador
        player_record["names"].add(player_name)
        player_record["sources"].add("tennis-api")
        if canonical_id != player_id:
            player_record["alternate_ids"].add(player_id)

        # Processa surface_summary
        surface_summary_data = player_full_data.get('surface_summary', {}).get('data', [])
        if surface_summary_data:
            # A API retorna um array de anos, cada um com um array de superfícies
            for year_data in surface_summary_data:
                for surface_stats in year_data.get('surfaces', []):
                    surface_name = surface_stats.get('court', 'unknown').lower()
                    # Para evitar sobreescrever, podemos agregar, mas por agora vamos pegar o mais recente
                    if surface_name not in player_record["stats"]["surface"]:
                         player_record["stats"]["surface"][surface_name] = surface_stats


        # Processa past_matches
        past_matches = player_full_data.get('past_matches', {}).get('data', [])
        if past_matches:
            # Apenas adiciona se não tivermos jogos ainda para evitar duplicatas massivas
            if not player_record["past_matches"]:
                 player_record["past_matches"] = past_matches

        # Processa ranking_data
        if 'ranking_data' in player_info and not player_record.get("ranking_data"):
            player_record["ranking_data"] = player_info['ranking_data']


def main():
    """Função principal para ler, processar e unificar os dados."""
    unified_stats = {}
    name_to_id_map = {}
    
    # Carrega o mapa de nomes do stats.csv
    # Usando o caminho relativo a partir da raiz do projeto, assumindo que os dados estão em 'dados/clean'
    player_name_map = load_player_name_map('dados/clean/stats.csv')
    
    # Ordem de processamento é importante:
    # 1. Tennis-API (stats2, stats3) para estabelecer IDs numéricos como canônicos.
    # 2. Ultimate-Tennis (stats_raw_*) para mesclar dados usando os nomes.
    files_to_process = [
        ('dados/raw/stats2_raw.json', process_stats_tennis_api),
        ('dados/raw/stats3_raw.json', process_stats_tennis_api),
        # Simulei um stats_raw_clay.json, mas o seu original é _hard.json. Ajuste conforme necessário.
        ('dados/raw/stats_raw_hard.json', process_stats_ultimate_tennis), 
    ]
    
    for file_path, process_func in files_to_process:
        if os.path.exists(file_path):
            print(f"\nLendo arquivo: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if process_func == process_stats_tennis_api:
                    process_func(data, unified_stats, name_to_id_map)
                else:
                    # Passa o mapa de nomes extra para a função da Ultimate Tennis
                    process_func(data, unified_stats, name_to_id_map, player_name_map)
        else:
            print(f"Aviso: Arquivo {file_path} não encontrado. Pulando.")
            
    # Pós-processamento final
    final_data = {}
    for player_id, data in unified_stats.items():
        # Converte sets para listas para que possam ser salvos em JSON
        data['names'] = sorted(list(data['names']))
        data['sources'] = sorted(list(data['sources']))
        data['alternate_ids'] = sorted(list(data['alternate_ids']))
        data['last_updated_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        # Cria um conjunto de nomes normalizados para mapeamento futuro
        data['normalized_names'] = sorted(list(set(normalize_player_name_for_key(name) for name in data['names'])))
        final_data[str(player_id)] = data
        
    # Salvar o arquivo unificado
    output_dir = 'dados/clean'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'stats_unified.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print(f"\nProcessamento concluído!")
    print(f"Total de {len(final_data)} jogadores únicos unificados.")
    print(f"Arquivo consolidado salvo em: {output_path}")

if __name__ == "__main__":
    main()