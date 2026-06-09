import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

def main():
    #save paths to datasets
    datasets = ['data/play_by_play_1999.csv.gz','data/play_by_play_2000.csv.gz','data/play_by_play_2001.csv.gz',
                'data/play_by_play_2002.csv.gz','data/play_by_play_2003.csv.gz','data/play_by_play_2004.csv.gz',
                'data/play_by_play_2005.csv.gz','data/play_by_play_2006.csv.gz','data/play_by_play_2007.csv.gz',
                'data/play_by_play_2008.csv.gz','data/play_by_play_2009.csv.gz','data/play_by_play_2010.csv.gz',
                'data/play_by_play_2011.csv.gz','data/play_by_play_2012.csv.gz','data/play_by_play_2013.csv.gz',
                'data/play_by_play_2014.csv.gz','data/play_by_play_2015.csv.gz','data/play_by_play_2016.csv.gz',
                'data/play_by_play_2017.csv.gz','data/play_by_play_2018.csv.gz','data/play_by_play_2019.csv.gz',
                'data/play_by_play_2020.csv.gz','data/play_by_play_2021.csv.gz','data/play_by_play_2022.csv.gz', 
                'data/play_by_play_2023.csv.gz','data/play_by_play_2024.csv.gz','data/play_by_play_2025.csv.gz']
    years = list(range(1999,2026))
    #years = [str(item) for item in years]

    #save fpts for use later
    df_fpts = pd.DataFrame()

    #save all data to one dataframe
    qb_historical = pd.DataFrame()

    #iterate through all pbp datasets to create season level summary datasets for individual player statistics
    for dataset, year in zip(datasets, years):

        #read dataset
        df = pd.read_csv(dataset)

        #calculate number of two point conversions when passing for fpts calculation
        df = calculate_two_pt_conv(df)

        #filter on regular season games
        df = df.query("season_type == 'REG'")

        #create dataframe with relevant stats
        relevant_stats = df[['yards_gained', 'passer_player_name', 'complete_pass', 'passer_player_id', 
                            'passing_yards', 'pass_attempt', 'pass_touchdown', 'first_down_pass',
                            'epa', 'yards_after_catch', 'air_epa', 'yac_epa', 'air_wpa', 'yac_wpa',
                            'interception', 'two_point_conv_score', 'sack', 'rush_touchdown', 'rushing_yards',
                            'rush', 'rusher_id', 'rusher_player_name', 'fumble_lost', 'fumble', 'fumbled_1_team',
                            'fumble_recovery_1_team']].copy()
        
        #generate fumble to turnover stat for fpts calc
        relevant_stats['qb_fumble_to_turnover'] = np.where(((relevant_stats['fumble'] == 1) & (relevant_stats['fumbled_1_team'].fillna('') != relevant_stats['fumble_recovery_1_team'].fillna('')) & (relevant_stats['complete_pass'] == 0) & (relevant_stats['rush'] == 0)), 1, 0)

        #group by name and derive relevant metrics for passing
        passer_df = relevant_stats.groupby('passer_player_name', as_index=False).agg(
            player_id=('passer_player_id', 'first'),
            total_passing_yards=('passing_yards', 'sum'),
            pass_yds_per_attempt=('passing_yards', 'mean'),
            pass_attempts=('pass_attempt', 'sum'),
            passing_tds=('pass_touchdown', 'sum'),
            first_down_passes=('first_down_pass', 'sum'),
            cmp=('complete_pass', 'sum'),
            ints=('interception', 'sum'),
            cmp_percentage=('complete_pass', 'mean'),
            epa=('epa', 'mean'),
            yac_sum=('yards_after_catch', 'sum'),
            yac_avg=('yards_after_catch', 'mean'),
            air_epa_avg=('air_epa', 'mean'),
            yac_epa_avg=('yac_epa', 'mean'),
            air_wpa_avg=('air_wpa', 'mean'),
            yac_wpa_avg=('yac_wpa', 'mean'),
            two_pt_sum=('two_point_conv_score', 'sum'),
            sacks=('sack', 'sum'),
            fumbles=('fumble_lost', 'sum'),
            fumbles_to_turnovers=('qb_fumble_to_turnover', 'sum')
        )

        passer_df['td_rate'] = passer_df['passing_tds']/passer_df['pass_attempts']
        passer_df['int_rate'] = passer_df['ints']/passer_df['pass_attempts']

        rusher_df = relevant_stats.groupby('rusher_player_name', as_index=False).agg(
            player_id=('rusher_id', 'first'),
            rushing_tds=('rush_touchdown', 'sum'),
            rushing_yds_sum=('rushing_yards', 'sum'),
            rushing_yds_avg=('rushing_yards', 'mean')
        )

        #merge passing and rushing stats on player_id, with only ids in the passing df being retained
        merged = pd.merge(passer_df, rusher_df, on='player_id', how='left').fillna(0)
        
        #drop players with fewer than 10 pass attempts
        merged = merged.query('pass_attempts > 10').reset_index(drop=True)

        #calculate qb fantasy points
        merged['cur_fpts'] = calculate_fpts(merged)
        
        #add year to dataset
        merged['year'] = year

        #concat yearly datasets
        if str(year) == '1999':
            qb_historical = merged.copy()
        else:
            qb_historical = pd.concat([qb_historical, merged], ignore_index=True)

        #store fpts later addition to datasets
        df_add_fpts = merged[['player_id', 'cur_fpts']]

        year_name = 'fpts_' + str(year)
        df_add_fpts.columns = ['player_id', year_name]

        if str(year) == '1999':
            df_fpts = df_add_fpts.copy()
        else:
            df_fpts = pd.merge(df_fpts, df_add_fpts, on='player_id', how='outer').fillna(0)


    future_fpts = create_future_fpts(qb_historical)
    qb_historical = add_future_fpts(qb_historical, future_fpts)

    #save dataset
    dataset_name = 'data/qb_historical.csv'
    qb_historical.to_csv(dataset_name, index=False)




#HELPER FUNCTIONS

def calculate_two_pt_conv(df):
    df['two_point_conv_score'] = np.where((df['two_point_conv_result'] == 'success'), 1, 0)

    return(df)

def calculate_fpts(df):

    fpts = ((df['total_passing_yards'] / 25) + (df['passing_tds'] * 4) - 
    (df['ints'] * 2) + (df['two_pt_sum'] * 2) - (df['fumbles_to_turnovers'] * 2) + 
    (df['rushing_yds_sum'] / 10) + (df['rushing_tds'] * 6))

    return(fpts)

def add_future_fpts(qb_historical, future_pts):
    
    merged = qb_historical.merge(future_pts, on=['player_id', 'year'],how='left')
    return(merged)

def create_future_fpts(qb_historical):

    future_fpts = qb_historical[['player_id', 'year', 'cur_fpts']].copy()

    future_fpts['year'] = future_fpts['year'] - 1

    future_fpts = future_fpts.rename(columns={'cur_fpts': 'next_fpts'})

    return(future_fpts)

def reshape_fpts_dataset(df_fpts):

    fpts_cols = [c for c in df_fpts.columns if c.startswith('fpts_')]

    future_fpts = df_fpts.melt(
        id_vars='player_id',
        value_vars=fpts_cols,
        var_name='fpts_year',
        value_name='next_fpts'
    )

    future_fpts['year'] = (
        future_fpts['fpts_year']
        .str.replace('fpts_', '', regex=False)
        .astype(int)
    )

    future_fpts['year'] -= 1

    future_fpts = future_fpts[['player_id', 'year', 'next_fpts']]

    print(future_fpts.head())
    return(future_fpts)


if __name__ == '__main__':
    main()

