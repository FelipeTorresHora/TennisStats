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
    aces = df_aces.sort_values(by='AvgAcesPerMatchSortField', ascending=False).iloc[:15].reset_index(drop=True)
    aces.index = aces.index + 1
    print (aces)

def aces():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_acesp = df[['PlayerName', 'AvgAcesPerMatch']]
    acesp = df_acesp.sort_values(by='AvgAcesPerMatch', ascending=False).iloc[:15].reset_index(drop=True)
    acesp.index = acesp.index + 1
    print (acesp)

def first_serve():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_first_serve = df[['PlayerName', 'FirstServePctSortField']]
    first_serve = df_first_serve.sort_values(by='FirstServePctSortField', ascending=False).iloc[:15].reset_index(drop=True)
    first_serve.index = first_serve.index + 1
    print (first_serve)

def first_serve_pct():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_first_serve_pct = df[['PlayerName', 'FirstServePointsWonPctSortField']]
    first_serve_pct = df_first_serve_pct.sort_values(by='FirstServePointsWonPctSortField', ascending=False).iloc[:15].reset_index(drop=True)
    first_serve_pct.index = first_serve_pct.index + 1
    print (first_serve_pct)

def double_fault():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_double_fault = df[['PlayerName', 'AvgDblFaultsPerMatchSortField']]
    double_fault = df_double_fault.sort_values(by='AvgDblFaultsPerMatchSortField', ascending=False).iloc[:15].reset_index(drop=True)
    double_fault.index = double_fault.index + 1
    print (double_fault)

def second_service():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_second_service = df[['PlayerName', 'SecondServePointsWonPctSortField']]
    second_service = df_second_service.sort_values(by='SecondServePointsWonPctSortField', ascending=False).iloc[:15].reset_index(drop=True)
    second_service.index = second_service.index + 1
    print (second_service)    

def servicewon():
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df_aces = df[['PlayerName', 'ServiceGamesWonPctSortField']]
    ser_won = df_aces.sort_values(by='ServiceGamesWonPctSortField', ascending=False).iloc[:15].reset_index(drop=True)
    ser_won.index = ser_won.index + 1
    print (ser_won)
