import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

def main():
    #save paths to datasets
    datasets = ['data/play_by_play_2022.csv.gz', 'data/play_by_play_2023.csv.gz', 'data/play_by_play_2024.csv.gz'
                'data/play_by_play_2025.csv.gz']

    #TODO delete when done testing
    datasets = ['data/play_by_play_2025.csv.gz'] 

    #iterate through all pbp datasets to create season level summary datasets for individual player statistics
    for dataset in datasets:

        #read dataset
        df = pd.read_csv(dataset)

        #calcualte number of two point conversions when passing for fpts calculation
        df = calculate_two_pt_passes(df)

        #filter on regular season games
        df = df.query("season_type == 'REG'")

        #create dataframe with relevant stats
        passing = df[['yards_gained', 'passer_player_name', 'complete_pass', 'passer_player_id', 
                            'passing_yards', 'pass_attempt', 'pass_touchdown', 'first_down_pass',
                            'epa', 'yards_after_catch', 'air_epa', 'yac_epa', 'air_wpa', 'yac_wpa',
                            'interception', 'two_point_conv_points', 'sack']]

        #group by name and derive relevant metrics
        passer_df = passing.groupby('passer_player_name', as_index=False).agg(
            player_id=('passer_player_id', 'first'),
            total_yards=('yards_gained', 'sum'),
            average_yards=('yards_gained', 'mean'),
            pass_attempts=('pass_attempt', 'sum'),
            touchdowns=('pass_touchdown', 'sum'),
            first_downs=('first_down_pass', 'sum'),
            completions=('complete_pass', 'sum'),
            interceptions=('interception', 'sum'),
            comp_percentage=('complete_pass', 'mean'),
            epa=('epa', 'mean'),
            yac_sum=('yards_after_catch', 'sum'),
            yac_avg=('yards_after_catch', 'mean'),
            air_epa_avg=('air_epa', 'mean'),
            yac_epa_avg=('yac_epa', 'mean'),
            air_wpa_avg=('air_wpa', 'mean'),
            yac_wpa_avg=('yac_wpa', 'mean'),
            two_pt_passing_sum=('two_point_conv_points', 'sum'),
            sacks=('sack', 'sum')
        )
        #TODO: handle two point rushing fantasy points when calculating rushing stats
        
        #drop players with fewer than 10 pass attempts
        passer_df = passer_df.query('pass_attempts > 10').reset_index(drop=True)

        #calculate passing fantasy points
        passer_df['fpts'] = calculate_fpts(passer_df)



#HELPER FUNCTIONS

def calculate_two_pt_passes(df):
    df['two_point_conv_points'] = np.where((df['pass'] == 1) &
                                        (df['two_point_conv_result'] == 'success'),
                                        1,
                                        0)
    return(df)

def calculate_fpts(df):
    passing_fpts = (df['total_yards'] / 25) + (df['touchdowns'] * 4) - (df['interceptions'] * 2) - (df['sacks'] * 1)

    return(passing_fpts)


if __name__ == '__main__':
    main()

