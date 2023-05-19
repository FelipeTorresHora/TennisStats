#!/usr/bin/env python
# coding: utf-8

# In[194]:


import requests
import pandas as pd

def get_data(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful
    data = response.json()['data']
    df = pd.DataFrame(data)
    df = df.drop(columns=['ID', 'Rank'])
    return df

url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/breakpointsconverted/2023/all"

headers = {
    "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
}
df = get_data(url, headers)
df['Percentage'] = df['Percentage'].str.rstrip('%').astype(float)
df = df.drop(columns=['Points Won','Matches','Total Points'])
filtered_df = df[df['Percentage'] > 40.18]
display(filtered_df)


# In[196]:



url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/servicegameswon/2023/all"

headers = {
    "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
}

df = get_data(url, headers)
df['Percentage'] = df['Percentage'].str.rstrip('%').astype(float)
df = df.drop(columns=['Games Won','Matches','Total Games'])
filtered_df2 = df[df['Percentage'] >82.39]
display(filtered_df2)


# In[198]:


url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/aces/2023/all"

headers = {
    "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
}

df = get_data(url, headers)
df = df.drop(columns=['Games played'])

# Converter a coluna 'Aces' de string para inteiro
df['Aces'] = df['Aces'].astype(int)
filtered_df3 = df[df['Aces'] >176]
display(filtered_df3)


# In[203]:


url = "https://ultimate-tennis1.p.rapidapi.com/global_players_stats/1stserve/2023/all"

headers = {
    "X-RapidAPI-Key": "743d67516fmsh1c6f10058aec683p1ae6a3jsna3a372a01620",
    "X-RapidAPI-Host": "ultimate-tennis1.p.rapidapi.com"
}

df = get_data(url, headers)
df['1st Serve percentage'] = df['1st Serve percentage'].str.rstrip('%').astype(float)
df = df.drop(columns=['Games played'])
filtered_df4 = df[df['1st Serve percentage'] >64]
print(filtered_df4)


# In[ ]:


#mais breaks e serviços confirmados
df_merged = pd.merge(filtered_df, filtered_df2, on='Name', how='inner')
df_merged


# In[ ]:


#serviçoes e aces
df_merged2 = pd.merge(filtered_df3, filtered_df2, on='Name', how='inner')
df_merged2


# In[ ]:


#serviçoes,aces e 1 serviço
df_merged3 = pd.merge(pd.merge(filtered_df3, filtered_df2, on='Name'), filtered_df4, on='Name')
df_merged3

