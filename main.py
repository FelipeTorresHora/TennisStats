import json
import os
from api.odds import run_data_pipeline
from api.stats import collect_all_players_data
from analise.analise_dados import *

def run_full_pipeline():
    """
    Executa o pipeline completo de coleta e análise de dados de tênis:
    1. Coleta estatísticas dos jogadores
    2. Coleta torneios ativos e odds
    3. Cruza dados de estatísticas com odds
    4. Gera relatório final
    """
    print("=== INICIANDO PIPELINE COMPLETO DE DADOS DE TÊNIS ===\n")
    
    # 1. Verificar se dados de stats já existem
    stats_clean_path = "dados/clean/stats_clean.json"
    if not os.path.exists(stats_clean_path):
        print("1. 📊 COLETANDO ESTATÍSTICAS DOS JOGADORES...")
        collect_all_players_data()
        print("   ✅ Coleta de estatísticas concluída\n")
    else:
        print("1. 📊 Arquivo de estatísticas já existe, pulando coleta...\n")
    
    # 2. Coletar torneios ativos e odds
    print("2. 🎾 COLETANDO TORNEIOS ATIVOS E ODDS...")
    collected_data, total_requests = run_data_pipeline()
    print(f"   ✅ Pipeline de odds concluído ({total_requests} requisições)\n")
    
    # 3. Cruzar dados (já feito automaticamente no pipeline de odds)
    print("3. 🔄 CRUZAMENTO DE DADOS...")
    if collected_data:
        print(f"   ✅ {len(collected_data)} eventos coletados com estatísticas e odds cruzadas\n")
    else:
        print("   ⚠️ Nenhum evento foi coletado\n")
    
    # 4. Gerar relatório
    print("4. 📋 GERANDO RELATÓRIO FINAL...")
    generate_final_report(collected_data, total_requests)
    
    print("=== PIPELINE COMPLETO FINALIZADO ===")
    return collected_data, total_requests

def generate_final_report(collected_data, total_requests):
    """Gera relatório final do pipeline"""
    
    print("\n--- RELATÓRIO FINAL ---")
    print(f"Total de requisições à API: {total_requests}")
    print(f"Total de eventos coletados: {len(collected_data) if collected_data else 0}")
    
    if collected_data:
        # Estatísticas por torneio
        tournaments = {}
        events_with_stats = 0
        events_with_odds = 0
        
        for event in collected_data:
            tournament_name = event.get('tournament_name', 'N/A')
            if tournament_name not in tournaments:
                tournaments[tournament_name] = 0
            tournaments[tournament_name] += 1
            
            # Contar eventos com estatísticas
            p1_stats = event.get('participant1', {}).get('stats')
            p2_stats = event.get('participant2', {}).get('stats')
            if p1_stats != "N/A" or p2_stats != "N/A":
                events_with_stats += 1
            
            # Contar eventos com odds
            if event.get('odds_bet365'):
                events_with_odds += 1
        
        print(f"\nEventos por torneio:")
        for tournament, count in tournaments.items():
            print(f"  • {tournament}: {count} eventos")
        
        print(f"\nEstatísticas de qualidade dos dados:")
        print(f"  • Eventos com estatísticas: {events_with_stats}/{len(collected_data)}")
        print(f"  • Eventos com odds: {events_with_odds}/{len(collected_data)}")
        
        # Salvar arquivo final
        output_file = "dados/clean/collected_tennis_data_atp_singles_pregame_with_stats.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(collected_data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Dados finais salvos em: {output_file}")
        except IOError as e:
            print(f"❌ Erro ao salvar arquivo final: {e}")
    
    else:
        print("\n⚠️ Nenhum dado foi coletado. Verifique:")
        print("  • Configuração das APIs (.env)")
        print("  • Disponibilidade de torneios ATP Singles")
        print("  • Filtros aplicados")

if __name__ == "__main__":
    run_full_pipeline()