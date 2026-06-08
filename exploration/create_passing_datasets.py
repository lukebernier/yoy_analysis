import pandas as pd

#save paths to datasets
datasets = ['data/play_by_play_2022.csv.gz', 'data/play_by_play_2023.csv.gz', 'data/play_by_play_2024.csv.gz'
            'data/play_by_play_2025.csv.gz']

#TODO delete when done testing
datasets = ['data/play_by_play_2025.csv.gz'] 

#iterate through all pbp datasets to create season level summary datasets for individual player statistics
for dataset in datasets:
    df = pd.read_csv(dataset)

    #create dataframe with relevant stats
    passing = df[['yards_gained', 'passer_player_name', 'complete_pass', 'passer_player_id', 
                        'passing_yards', 'pass_attempt', 'pass_touchdown', 'first_down_pass',
                        'epa', 'yards_after_catch', 'air_epa', 'yac_epa', 'air_wpa', 'yac_wpa']]
    
    #group by name and derive relevant metrics
    passer_df = passing.groupby('passer_player_name', as_index=False).agg(
        player_id=('passer_player_id', 'first'),
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
    
    #drop players with fewer than 10 pass attempts
    passer_df = passer_df.query('pass_attempts > 10').reset_index(drop=True)

print(passer_df.info())