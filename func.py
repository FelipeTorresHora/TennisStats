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
print(df.info())
#PlayerName, AvgAcesPerMatchSortField, AvgDblFaultsPerMatchSortField, FirstServePctSortField, ServiceGamesWonPctSortField


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
    return aces

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
    return ser_won