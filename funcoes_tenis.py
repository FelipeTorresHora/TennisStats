import requests
import pandas as pd

def get_data(url, headers):
    """ 
    Esta função é usada para buscar dados de um determinado URL usando a biblioteca de solicitações.
    São necessários dois parâmetros: url e headers. O URL é o ponto final de onde os dados devem ser obtidos.
    O parâmetro headers é um dicionário que contém os headers a serem enviados com a solicitação.
    Os dados extraídos são então convertidos em um DataFrame do pandas.
    O DataFrame é então modificado para eliminar as colunas ID e Rank, pois são dispensáveis para a análise.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()  
    data = response.json()['data']
    df = pd.DataFrame(data)
    df = df.drop(columns=['ID', 'Rank'])
    return df
def break_points_converted():
    """
    Essa função é usada para buscar os dados dos jogadores com melhores break points convertidos.
    Os dados são solicitados na API e são tratados de acordo com a necessidade. 
    """
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/breakpointsconverted/2023/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }
    df = get_data(url, headers)
    df['Percentage'] = df['Percentage'].str.rstrip('%').astype(float)
    df = df.drop(columns=['Points Won','Matches','Total Points'])
    filtered_df = df[df['Percentage'] > 40.18]
    print (filtered_df)
    
def saques_vencidos():  
    """
    Essa função é usada para buscar os dados dos jogadores com mais games de saque vencidos.
    Os dados são solicitados na API e são tratados de acordo com a necessidade. 
    """
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/servicegameswon/2023/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }

    df = get_data(url, headers)
    df['Percentage'] = df['Percentage'].str.rstrip('%').astype(float)
    df = df.drop(columns=['Games Won','Matches','Total Games'])
    filtered_df2 = df[df['Percentage'] >82.39]
    print (filtered_df2)

def aces():
    """
    Essa função é usada para buscar os dados dos jogadores com mais aces durante o ano.
    Os dados são solicitados na API e são tratados de acordo com a necessidade. 
    """
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/aces/2023/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }
    df = get_data(url, headers)
    df = df.drop(columns=['Games played'])
    df['Aces'] = df['Aces'].str.replace(",","")
    df['Aces'] = df['Aces'].astype(int) 
    filtered_df3 = df[df['Aces'] > 207]
    print (filtered_df3)


def primeiro_servico():
    """
    Essa função é usada para buscar os dados dos jogadores com mais primeiros serviços acertados.
    Os dados são solicitados na API e são tratados de acordo com a necessidade. 
    """
    url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/1stserve/2023/all"
    headers = {
        "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
        "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
    }
    df = get_data(url, headers)
    df['1st Serve percentage'] = df['1st Serve percentage'].str.rstrip('%').astype(float)
    df = df.drop(columns=['Games played'])
    filtered_df4 = df[df['1st Serve percentage'] >64]
    print (filtered_df4)