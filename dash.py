from func import *
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

stats_options = {
        'Média de aces por jogo': aces_avg,
        'Primeiro Serviço': first_serve,
        'Porcentagem de Pontos ganhos com primeiro Serviço': first_serve_pct,
        'Média de Dupla Falta Por Jogo': double_fault,
        'Pontos Ganhos Segundo Serviço': second_service,
        'Porcentagem Games De Saques Ganhos': servicewon
}
    
#Cria interface principal
st.title("Estatísticas de Tenistas ATP")
st.write("A aplicação irá mostrar todas estatísticas de torneios feitos pela ATP no ano de 2024")
stat_choice = st.sidebar.selectbox('Escolha a estatística para visualizar:', list(stats_options.keys()))

# Chama a função correspondente à escolha do usuário
stat_df = stats_options[stat_choice]()

# Exibir os dados em uma tabela
st.subheader(f"Tabela de {stat_choice}")
st.dataframe(stat_df)

# Exibir os dados em um gráfico de barras
st.subheader(f"Gráfico de {stat_choice}")
fig, ax = plt.subplots()
ax.bar(stat_df['Nome do Jogador'], stat_df.iloc[:, 1], color='skyblue')
    
# Melhorar a visualização do gráfico
plt.xticks(rotation=45, ha='right')  # Rotaciona os nomes dos jogadores
plt.tight_layout()
    
# Mostrar o gráfico no Streamlit
st.pyplot(fig)
