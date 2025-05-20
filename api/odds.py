#!/usr/bin/env python3
import os
import requests
import pandas as pd

API_HOST = "odds-api1.p.rapidapi.com"
API_KEY  = "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620"

EVENTS_CSV = "dados/events.csv"
ODDS_CSV   = "dados/odds.csv"

def fetch_event_data(event_id: str) -> dict:
    url = f"https://{API_HOST}/odds"
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key":  API_KEY,
    }
    params = {
        "eventId":     event_id,
        "bookmakers":  "bet365",
        "oddsFormat":  "decimal",
        "raw":         "false",
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def build_event_df(data: dict) -> pd.DataFrame:
    evt = {
        "event_id":      data["eventId"],
        "betradar_id":   data["betradarId"],
        "date":          data["date"],
        "time":          data["time"],
        "participant1":  data["participant1"],
        "participant2":  data["participant2"],
        "status":        data["eventStatus"],
        "sport":         data["sportSlug"],
    }
    return pd.DataFrame([evt])

def build_odds_df(data: dict) -> pd.DataFrame:
    rows = []
    for mkt_id, mkt in data["markets"].items():
        for out_id, out in mkt["outcomes"].items():
            odds = out["bookmakers"]["bet365"]["price"]
            if odds <= 1.30:
                continue
            rows.append({
                "event_id":   data["eventId"],
                "market":     mkt["marketName"],
                "short":      mkt["marketNameShort"],
                "handicap":   mkt["handicap"],
                "odds_type":  mkt["oddsType"],
                "outcome":    out["outcomeName"],
                "odds":       odds,
            })
    return pd.DataFrame(rows)

def append_if_new(df: pd.DataFrame, csv_path: str, key: str) -> bool:
    """
    Se csv não existir, cria e grava df.
    Se existir, verifica se valor df[key][0] já está em csv[key];
    se não, faz append. Retorna True se gravou, False se já existia.
    """
    if not os.path.isfile(csv_path):
        df.to_csv(csv_path, index=False)
        return True
    existing = pd.read_csv(csv_path, dtype=str)
    if df.iloc[0][key] in existing[key].astype(str).values:
        return False
    df.to_csv(csv_path, mode="a", header=False, index=False)
    return True

def main(event_id: str):
    data = fetch_event_data(event_id)
    evt_df  = build_event_df(data)
    odds_df = build_odds_df(data)

    wrote_event = append_if_new(evt_df,  EVENTS_CSV, "event_id")
    if wrote_event:
        append_if_new(odds_df, ODDS_CSV, "event_id")
        print(f"Novo evento '{event_id}' adicionado a '{EVENTS_CSV}' e suas odds a '{ODDS_CSV}'.")
    else:
        print(f"Evento '{event_id}' já existe em '{EVENTS_CSV}'. Nada foi alterado.")

if __name__ == "__main__":
    event_id = "id1201231560558135"
    if not event_id:
        print("Erro: é preciso informar um event_id válido.")
        exit(1)
    main(event_id)