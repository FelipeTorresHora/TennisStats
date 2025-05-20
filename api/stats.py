#!/usr/bin/env python3
import requests
import pandas as pd

# Constantes da API
STATS_URL = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/serve/2024/all"
LB_URL    = "https://ultimate-tennis1.p.rapidapi.com/live_leaderboard/150"
HEADERS = {
    "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
}

def fetch_stats() -> pd.DataFrame:
    """Busca estatísticas de saque de todos os jogadores."""
    resp = requests.get(STATS_URL, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return pd.DataFrame(data)

def preprocess_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Seleciona e renomeia colunas:
    - Remove as colunas de texto originais (não-‘SortField’)
    - Renomeia para português
    """
    cols = [
        "PlayerId",
        "PlayerName",
        "AvgAcesPerMatchSortField",
        "AvgDblFaultsPerMatchSortField",
        "FirstServePctSortField",
        "FirstServePointsWonPctSortField",
        "SecondServePointsWonPctSortField",
        "ServeRatingSortField",
        "ServiceGamesWonPctSortField",
    ]
    df = df[cols].rename(columns={
        "PlayerId":                         "IdJogador",
        "PlayerName":                       "NomeJogador",
        "AvgAcesPerMatchSortField":         "MediaAces",
        "AvgDblFaultsPerMatchSortField":    "MediaDuplaFalta",
        "FirstServePctSortField":           "PctPrimeiroServico",
        "FirstServePointsWonPctSortField":  "PctPontosPrimeiroServico",
        "SecondServePointsWonPctSortField": "PctPontosSegundoServico",
        "ServeRatingSortField":             "ClassificacaoSaque",
        "ServiceGamesWonPctSortField":      "PctGamesSaqueGanhos",
    })
    return df

def fetch_leaderboard() -> pd.DataFrame:
    """Busca ranking ao vivo e retorna apenas Rank, id e Name."""
    resp = requests.get(LB_URL, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    df = pd.DataFrame(data)
    return df[["Rank", "id", "Name"]].rename(columns={
        "Rank": "Rank",
        "id":   "Id",
        "Name": "NomeJogador"
    })

def main():
    # 1) Estatísticas de saque
    df_stats = preprocess_stats(fetch_stats())

    # 2) Ranking ao vivo
    df_rank = fetch_leaderboard()

    # 3) Merge pela coluna NomeJogador
    df = pd.merge(df_stats, df_rank, on="NomeJogador", how="left")

    # 4) Salvando em CSV
    df.to_csv("dados/stats.csv", index=False, encoding="utf-8-sig")
    print("Arquivo stats.csv gerado com sucesso!")

if __name__ == "__main__":
    main()