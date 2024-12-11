from func import *
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(
    page_title="Estatísticas ATP 2024",
    page_icon="🎾",
    layout="wide"
)

# Dicionário com as estatísticas e suas funções
stats_options = {
    'Média de aces por jogo': aces_avg,
    'Primeiro Serviço': first_serve,
    'Porcentagem de Pontos ganhos com primeiro Serviço': first_serve_pct,
    'Média de Dupla Falta Por Jogo': double_fault,
    'Pontos Ganhos Segundo Serviço': second_service,
    'Porcentagem Games De Saques Ganhos': servicewon
}

# Título principal e introdução
st.title("📊 Dashboard de Estatísticas ATP 2024")
st.markdown("---")

# Seção de Sobre o Projeto
st.header("📌 Sobre o Projeto")
st.write("""
Este dashboard apresenta análises estatísticas detalhadas dos jogadores da ATP (Association of Tennis Professionals) 
para o ano de 2024. Os dados são atualizados em tempo real através da API Ultimate Tennis, fornecendo insights 
valiosos sobre o desempenho dos jogadores em diferentes aspectos do jogo.
""")

# Explicação das Estatísticas
st.header("📈 Estatísticas Disponíveis")
st.markdown("""
Aqui está um guia detalhado de cada estatística disponível no dashboard:

**🎯 Média de Aces por Jogo**
- Indica a média de saques diretos (aces) que um jogador consegue por partida
- Demonstra a efetividade do saque do jogador e sua capacidade de conquistar pontos diretos

**🎾 Primeiro Serviço**
- Mostra a porcentagem de primeiros serviços que entram na quadra
- Indica a consistência do jogador no primeiro saque

**💪 Porcentagem de Pontos Ganhos com Primeiro Serviço**
- Representa a taxa de sucesso quando o primeiro serviço entra
- Demonstra a eficiência do jogador em vencer pontos com seu primeiro saque

**⚠️ Média de Dupla Falta Por Jogo**
- Indica quantas duplas faltas o jogador comete em média por partida
- Quanto menor este número, melhor é a consistência do saque do jogador

**🎯 Pontos Ganhos no Segundo Serviço**
- Mostra a porcentagem de pontos ganhos quando o jogador precisa usar o segundo serviço
- Indica a qualidade do "plano B" do jogador no saque

**🏆 Porcentagem de Games De Saques Ganhos**
- Representa a porcentagem de games que o jogador vence quando está sacando
- É um indicador importante da capacidade geral do jogador em defender seu saque
""")

# Sidebar para seleção de estatísticas
with st.sidebar:
    st.header("Seleção de Estatísticas")
    st.write("Escolha uma estatística para visualizar os dados:")
    stat_choice = st.selectbox('Estatística:', list(stats_options.keys()))

# Exibição dos dados escolhidos
if stat_choice:
    st.markdown("---")
    st.subheader(f"📊 {stat_choice}")
    
    # Obter os dados
    stat_df = stats_options[stat_choice]()
    
    # Criar colunas para organizar a visualização
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("Tabela de Dados")
        st.dataframe(stat_df)
    
    with col2:
        st.write("Visualização Gráfica")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(stat_df['Nome do Jogador'], stat_df.iloc[:, 1], color='#1f77b4')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

# Nota de rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <small>Desenvolvido com dados da API Ultimate Tennis • Atualizado em tempo real</small>
</div>
""", unsafe_allow_html=True)