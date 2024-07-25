import requests
import pandas as pd

def get_data(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful
    data = response.json()['data']
    df = pd.DataFrame(data)
    return df

url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
headers = {
    "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
}
df = get_data(url, headers)
# print(df.info())

df_aces = df[['PlayerName', 'AvgAcesPerMatchSortField']]

# Ordenar por aces em ordem decrescente e selecionar os 10 primeiros usando iloc
top_10_aces = df_aces.sort_values(by='AvgAcesPerMatchSortField', ascending=False).iloc[:20]
print(top_10_aces)

#PlayerName, AvgAcesPerMatchSortField, AvgDblFaultsPerMatchSortField, FirstServePctSortField, ServiceGamesWonPctSortField
#DROPAR TABELAS
#SORT POR TABELA E MOSTRAR SÓ OS VALORES DAQUELA COLUNA E DO TENISTA
# UI BONITA 







# url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/breakpointsconverted/2023/all"
# headers = {
#     "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
#     "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
# }
# df = get_data(url, headers)
# df['Percentage'] = df['Percentage'].str.rstrip('%').astype(float)
# df = df.drop(columns=['Points Won','Matches','Total Points'])
# filtered_df = df[df['Percentage'] > 40.18]

# url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/servicegameswon/2023/all"
# headers = {
#     "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
#     "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
# }

# df = get_data(url, headers)
# df['Percentage'] = df['Percentage'].str.rstrip('%').astype(float)
# df = df.drop(columns=['Games Won','Matches','Total Games'])
# filtered_df2 = df[df['Percentage'] >82.39]

# url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/aces/2023/all"
# headers = {
#     "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
#     "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
# }

# df = get_data(url, headers)
# df = df.drop(columns=['Games played'])

# # Converter a coluna 'Aces' de string para inteiro
# df['Aces'] = df['Aces'].astype(int)
# filtered_df3 = df[df['Aces'] >207]

# url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/1stserve/2023/all"
# headers = {
#     "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
#     "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
# }

# df = get_data(url, headers)
# df['1st Serve percentage'] = df['1st Serve percentage'].str.rstrip('%').astype(float)
# df = df.drop(columns=['Games played'])
# filtered_df4 = df[df['1st Serve percentage'] >64]

# while True:
#     op = input("1 = Breaks Convertidos 2 = Serviços ganhos 3 = Aces 4 = 1 saque procentagem: ")
#     if op == "1":
#         print(filtered_df)
#         break
#     elif op == "2":
#         print(filtered_df2)
#         break
#     elif op == "3":
#         print(filtered_df3)
#         break
#     elif op == "4":
#         print(filtered_df4)
#         break
#     else:
#         print("Inválido")
#         continue
    
#outlook = win32.Dispatch('outlook.application')
#email = outlook.CreateItem(0)
#email.To = 'fhora93@hotmail.com'
#email.Subject = 'Cotação do Mercado Financeiro'
#email.Body = f'''Prezado Diretor, segue o relatório diário:
#email.Send()
