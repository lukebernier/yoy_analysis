import pandas as pd
from collections import Counter


df = pd.read_csv('data/play_by_play_2025.csv.gz')

#print(df.info(verbose=True, show_counts=True))

passing_yards = df[['yards_gained', 'passer_player_name', 'complete_pass', 'passer_player_id', 
                    'passing_yards', 'pass_attempt', 'pass_touchdown', 'first_down_pass',
                    'epa', 'yards_after_catch', 'air_epa', 'yac_epa', 'air_wpa', 'yac_wpa']]

passing_yards = passing_yards.dropna(subset=["complete_pass"])

#print(passing_yards.info())

completed_passes = Counter(passing_yards['complete_pass'])
yg_counts = Counter(passing_yards['yards_gained'])

#print(completed_passes)
print(passing_yards.iloc[1000])

#passer_df = passing_yards.groupby('passer_player_name', as_index=False).sum()
passer_df = passing_yards.groupby('passer_player_name', as_index=False).agg(
    total_yards=('yards_gained', 'sum'),
    average_yards=('yards_gained', 'mean'),
    pass_attempts=('pass_attempt', 'sum'),
    touchdowns=('pass_touchdown', 'sum'),
    first_downs=('first_down_pass', 'sum'),
    completions=('complete_pass', 'sum'),
    comp_percentage=('complete_pass', 'mean'),
    epa=('epa', 'mean'),
    yac_sum=('yards_after_catch', 'sum'),
    yac_avg=('yards_after_catch', 'mean'),
    air_epa_avg=('air_epa', 'mean'),
    yac_epa_avg=('yac_epa', 'mean'),
    air_wpa_avg=('air_wpa', 'mean'),
    yac_wpa_avg=('yac_wpa', 'mean')
)
print(passer_df.info())

passer_df = passer_df.query('pass_attempts > 10').reset_index()

print(passer_df.info())
print(passer_df['passer_player_name'])
print(passer_df['comp_percentage'])

#print(passer_df['passer_player_name'])
#print(passer_df['pass_touchdown'])
#print(passer_df['yards_gained'])
#print(passer_df['complete_pass'])


