import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Import pipeline functions
from main import run_full_pipeline, generate_final_report
from api.odds import run_data_pipeline
from api.stats import collect_all_players_data

st.set_page_config(
    page_title="TennisStats Pipeline",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎾 TennisStats Data Pipeline")
st.markdown("---")

# Sidebar configuration
st.sidebar.title("⚙️ Configurações")

# Pipeline options
st.sidebar.header("Opções do Pipeline")
run_stats_collection = st.sidebar.checkbox("Coletar estatísticas dos jogadores", value=True)
run_odds_collection = st.sidebar.checkbox("Coletar torneios e odds", value=True)
generate_report = st.sidebar.checkbox("Gerar relatório final", value=True)

# API Configuration status
st.sidebar.header("Status da Configuração")
env_status = check_env_config()
for service, status in env_status.items():
    icon = "✅" if status else "❌"
    st.sidebar.write(f"{icon} {service}")

def check_env_config():
    """Verifica se as variáveis de ambiente estão configuradas"""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "RAPIDAPI_KEY": bool(os.getenv("RAPIDAPI_KEY")),
        "RAPIDAPI_HOST": bool(os.getenv("RAPIDAPI_HOST")),
        "STATS_RAPIDAPI_KEY": bool(os.getenv("STATS_RAPIDAPI_KEY"))
    }

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Executar Pipeline")
    
    if st.button("▶️ Executar Pipeline Completo", type="primary", use_container_width=True):
        run_pipeline()
    
    st.markdown("---")
    
    # Individual pipeline steps
    st.subheader("Executar Etapas Individuais")
    
    col_stats, col_odds = st.columns(2)
    
    with col_stats:
        if st.button("📊 Coletar Estatísticas", use_container_width=True):
            run_stats_only()
    
    with col_odds:
        if st.button("🎾 Coletar Odds", use_container_width=True):
            run_odds_only()

with col2:
    st.header("📋 Status dos Dados")
    display_data_status()

# Results section
st.markdown("---")
st.header("📊 Resultados e Visualizações")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "📄 Dados Brutos", "🏆 Torneios", "⚙️ Logs"])

with tab1:
    display_dashboard()

with tab2:
    display_raw_data()

with tab3:
    display_tournaments_info()

with tab4:
    display_logs()

def run_pipeline():
    """Executa o pipeline completo com feedback em tempo real"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.empty()
    
    # Capture stdout/stderr
    log_capture = StringIO()
    
    try:
        status_text.text("🚀 Iniciando pipeline completo...")
        progress_bar.progress(10)
        
        with redirect_stdout(log_capture), redirect_stderr(log_capture):
            collected_data, total_requests = run_full_pipeline()
        
        progress_bar.progress(100)
        status_text.text("✅ Pipeline executado com sucesso!")
        
        # Display results
        if collected_data:
            st.success(f"Pipeline concluído! {len(collected_data)} eventos coletados com {total_requests} requisições à API.")
            
            # Update session state
            st.session_state['last_run_data'] = collected_data
            st.session_state['last_run_requests'] = total_requests
            st.session_state['last_run_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            st.warning("Pipeline executado, mas nenhum dado foi coletado.")
        
        # Show logs
        logs = log_capture.getvalue()
        if logs:
            with log_container.container():
                st.text_area("Logs da Execução", logs, height=300)
    
    except Exception as e:
        st.error(f"Erro durante a execução: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Erro na execução")

def run_stats_only():
    """Executa apenas a coleta de estatísticas"""
    with st.spinner("Coletando estatísticas dos jogadores..."):
        try:
            collect_all_players_data()
            st.success("Coleta de estatísticas concluída!")
        except Exception as e:
            st.error(f"Erro na coleta de estatísticas: {str(e)}")

def run_odds_only():
    """Executa apenas a coleta de odds"""
    with st.spinner("Coletando torneios e odds..."):
        try:
            collected_data, total_requests = run_data_pipeline()
            if collected_data:
                st.success(f"Coleta de odds concluída! {len(collected_data)} eventos coletados.")
                st.session_state['last_odds_data'] = collected_data
            else:
                st.warning("Coleta executada, mas nenhum dado foi obtido.")
        except Exception as e:
            st.error(f"Erro na coleta de odds: {str(e)}")

def display_data_status():
    """Mostra o status atual dos arquivos de dados"""
    data_files = {
        "Stats Clean": "dados/clean/stats_clean.json",
        "Stats CSV": "dados/clean/stats.csv", 
        "Dados Finais": "dados/clean/collected_tennis_data_atp_singles_pregame_with_stats.json",
        "Stats Raw": "dados/raw/stats_raw.json",
        "Stats2 Raw": "dados/raw/stats2_raw.json"
    }
    
    for name, path in data_files.items():
        if os.path.exists(path):
            try:
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
                st.success(f"✅ {name}")
                st.caption(f"Tamanho: {size/1024:.1f}KB | Modificado: {modified}")
            except:
                st.success(f"✅ {name} (erro ao ler detalhes)")
        else:
            st.error(f"❌ {name}")

def display_dashboard():
    """Exibe dashboard com visualizações dos dados"""
    if 'last_run_data' in st.session_state:
        data = st.session_state['last_run_data']
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Eventos", len(data))
        
        with col2:
            tournaments = len(set(event.get('tournament_name', 'N/A') for event in data))
            st.metric("Torneios", tournaments)
        
        with col3:
            events_with_odds = sum(1 for event in data if event.get('odds_bet365'))
            st.metric("Eventos com Odds", events_with_odds)
        
        with col4:
            events_with_stats = sum(1 for event in data if 
                                  event.get('participant1', {}).get('stats') != "N/A" or 
                                  event.get('participant2', {}).get('stats') != "N/A")
            st.metric("Eventos com Stats", events_with_stats)
        
        # Gráfico de eventos por torneio
        tournament_counts = {}
        for event in data:
            tournament = event.get('tournament_name', 'N/A')
            tournament_counts[tournament] = tournament_counts.get(tournament, 0) + 1
        
        if tournament_counts:
            fig = px.bar(
                x=list(tournament_counts.keys()),
                y=list(tournament_counts.values()),
                title="Eventos por Torneio",
                labels={'x': 'Torneio', 'y': 'Número de Eventos'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de próximos jogos
        st.subheader("🎾 Próximos Jogos")
        games_data = []
        for event in data[:10]:  # Mostrar apenas os primeiros 10
            games_data.append({
                "Torneio": event.get('tournament_name', 'N/A'),
                "Jogador 1": event.get('participant1', {}).get('name_api', 'N/A'),
                "Jogador 2": event.get('participant2', {}).get('name_api', 'N/A'),
                "Data": event.get('event_date', 'N/A'),
                "Odds Disponíveis": "✅" if event.get('odds_bet365') else "❌"
            })
        
        if games_data:
            df_games = pd.DataFrame(games_data)
            st.dataframe(df_games, use_container_width=True)
    
    else:
        st.info("Execute o pipeline para ver as visualizações dos dados.")

def display_raw_data():
    """Exibe os dados brutos coletados"""
    if 'last_run_data' in st.session_state:
        data = st.session_state['last_run_data']
        
        st.subheader("Dados Coletados")
        st.caption(f"Última execução: {st.session_state.get('last_run_time', 'N/A')}")
        
        # Seletor de evento para detalhes
        if data:
            event_options = [f"{event.get('participant1', {}).get('name_api', 'N/A')} vs {event.get('participant2', {}).get('name_api', 'N/A')}" 
                           for event in data]
            
            selected_event_idx = st.selectbox("Selecione um evento para ver detalhes:", 
                                            range(len(event_options)), 
                                            format_func=lambda x: event_options[x])
            
            if selected_event_idx is not None:
                selected_event = data[selected_event_idx]
                st.json(selected_event)
        
        # Download dos dados
        if st.button("📥 Baixar Dados JSON"):
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="Baixar dados completos",
                data=json_str,
                file_name=f"tennis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("Execute o pipeline para ver os dados brutos.")

def display_tournaments_info():
    """Exibe informações detalhadas sobre torneios"""
    data_file = "dados/clean/collected_tennis_data_atp_singles_pregame_with_stats.json"
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Análise por torneio
            tournament_analysis = {}
            for event in data:
                tournament = event.get('tournament_name', 'N/A')
                if tournament not in tournament_analysis:
                    tournament_analysis[tournament] = {
                        'events': 0,
                        'with_odds': 0,
                        'with_stats': 0,
                        'category': event.get('tournament_category', 'N/A')
                    }
                
                tournament_analysis[tournament]['events'] += 1
                
                if event.get('odds_bet365'):
                    tournament_analysis[tournament]['with_odds'] += 1
                
                if (event.get('participant1', {}).get('stats') != "N/A" or 
                    event.get('participant2', {}).get('stats') != "N/A"):
                    tournament_analysis[tournament]['with_stats'] += 1
            
            # Tabela de análise
            analysis_data = []
            for tournament, stats in tournament_analysis.items():
                analysis_data.append({
                    "Torneio": tournament,
                    "Categoria": stats['category'],
                    "Total Eventos": stats['events'],
                    "Com Odds": f"{stats['with_odds']}/{stats['events']}",
                    "Com Stats": f"{stats['with_stats']}/{stats['events']}",
                    "% Completo": f"{min(stats['with_odds'], stats['with_stats'])/stats['events']*100:.1f}%"
                })
            
            df_analysis = pd.DataFrame(analysis_data)
            st.dataframe(df_analysis, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
    else:
        st.warning("Arquivo de dados não encontrado. Execute o pipeline primeiro.")

def display_logs():
    """Exibe área de logs do sistema"""
    st.subheader("📋 Logs do Sistema")
    
    # Log area for runtime information
    if 'pipeline_logs' not in st.session_state:
        st.session_state['pipeline_logs'] = []
    
    # Manual log input for testing
    if st.button("🧪 Adicionar Log de Teste"):
        test_log = f"[{datetime.now().strftime('%H:%M:%S')}] Pipeline test log entry"
        st.session_state['pipeline_logs'].append(test_log)
    
    # Display logs
    if st.session_state['pipeline_logs']:
        log_text = "\n".join(st.session_state['pipeline_logs'])
        st.text_area("Logs", log_text, height=300, disabled=True)
    else:
        st.info("Nenhum log disponível. Execute o pipeline para ver os logs.")
    
    # Clear logs button
    if st.button("🗑️ Limpar Logs"):
        st.session_state['pipeline_logs'] = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Desenvolvido com Streamlit 🎈 | TennisStats Pipeline v1.0")