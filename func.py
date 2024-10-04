import requests
import pandas as pd
import os

def clear_screen():
    # Limpa a tela do terminal
    os.system('cls' if os.name == 'nt' else 'clear')

def get_data(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    data = response.json()['data']
    df = pd.DataFrame(data)
    return df

def aces_avg():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_aces = df[['PlayerName', 'AvgAcesPerMatchSortField']]
    df_aces = df_aces.rename(columns={'PlayerName': 'Nome do Jogador', 'AvgAcesPerMatchSortField': 'Média de aces'})
    df_aces['Média de aces'] = df_aces['Média de aces'].astype(float)
    aces = df_aces.sort_values(by='Média de aces', ascending=False).iloc[:15].reset_index(drop=True)
    aces.index = aces.index + 1
    return aces

def acesa():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_acesp = df[['PlayerName', 'AvgAcesPerMatch']]
    df_acesp = df_acesp.rename(columns={'PlayerName': 'Nome do Jogador', 'AvgAcesPerMatch': 'Média de aces por jogo'})
    acesp = df_acesp.sort_values(by='Média de aces por jogo', ascending=False).iloc[:15].reset_index(drop=True)
    acesp.index = acesp.index + 1
    return acesp

def first_serve():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_first_serve = df[['PlayerName', 'FirstServePctSortField']]
    df_first_serve = df_first_serve.rename(columns={'PlayerName': 'Nome do Jogador', 'FirstServePctSortField': 'Primeiro Serviço'})
    first_serve = df_first_serve.sort_values(by='Primeiro Serviço', ascending=False).iloc[:15].reset_index(drop=True)
    first_serve.index = first_serve.index + 1
    return first_serve

def first_serve_pct():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_first_serve_pct = df[['PlayerName', 'FirstServePointsWonPctSortField']]
    df_first_serve_pct = df_first_serve_pct.rename(columns={'PlayerName': 'Nome do Jogador', 'FirstServePointsWonPctSortField': 'Porcentagem de Primeiro Serviço'})
    first_serve_pct = df_first_serve_pct.sort_values(by='Porcentagem de Primeiro Serviço', ascending=False).iloc[:15].reset_index(drop=True)
    first_serve_pct.index = first_serve_pct.index + 1
    return first_serve_pct

def double_fault():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_double_fault = df[['PlayerName', 'AvgDblFaultsPerMatchSortField']]
    df_double_fault = df_double_fault.rename(columns={'PlayerName': 'Nome do Jogador', 'AvgDblFaultsPerMatchSortField': 'Média de Dupla Falta Por Jogo'})
    double_fault = df_double_fault.sort_values(by='Média de Dupla Falta Por Jogo', ascending=False).iloc[:15].reset_index(drop=True)
    double_fault.index = double_fault.index + 1
    return double_fault

def second_service():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_second_service = df[['PlayerName', 'SecondServePointsWonPctSortField']]
    df_second_service = df_second_service.rename(columns={'PlayerName': 'Nome do Jogador', 'SecondServePointsWonPctSortField': 'Pontos Ganhos Segundo Serviço'})
    second_service = df_second_service.sort_values(by='Pontos Ganhos Segundo Serviço', ascending=False).iloc[:15].reset_index(drop=True)
    second_service.index = second_service.index + 1
    return second_service    

def servicewon():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_aces = df[['PlayerName', 'ServiceGamesWonPctSortField']]
    df_aces = df_aces.rename(columns={'PlayerName': 'Nome do Jogador', 'ServiceGamesWonPctSortField': 'Porcentagem Games De Saques Ganhos'})
    ser_won = df_aces.sort_values(by='Porcentagem Games De Saques Ganhos', ascending=False).iloc[:15].reset_index(drop=True)
    ser_won.index = ser_won.index + 1
    return ser_won