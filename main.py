import pickle
import pandas as pd
from collections import defaultdict
import numpy as np
from math import sqrt
import os
from itertools import product
from colorama import Fore
from math import sqrt
from statistics import stdev

STATS_CONSIDERED = ['yards_gained',
                    'air_yards', 'complete_pass', 'interception', 'pass_attempt',
                    'first_down_pass', 'first_down_rush', 'third_down_converted', 'third_down_failed', 'fourth_down_converted', 'fourth_down_failed',
                    'touchdown', 'pass_touchdown', 'rush_touchdown',
                    'qb_hit', 'sack', 'fumble', 'safety',
                    'no_huddle', 'qb_dropback', 'qb_spike', 'qb_scramble', 'shotgun',
                    'penalty_yards', 'penalty', 'replay_or_challenge',
                    'air_epa', 'yac_epa', 'epa']
BASIC_COLS = ['game_id', 'posteam', 'passer_player_name', 'play_type', 'home_team',
              'away_team', 'total_home_score', 'total_away_score', 'game_seconds_remaining',
              'season', 'two_point_attempt', 'extra_point_attempt']

def strip_unnecessary_columns(df):
    for col in df.columns:
        if col not in BASIC_COLS + STATS_CONSIDERED:
            del df[col]

def process_QB_play(df, time_length=3600):
    stats_dict = {}
    stats_dict['time_length'] = time_length
    stats_dict['team'] = df['posteam'].iloc[0]
    stats_dict['season'] = df['season'].iloc[0]
    if time_length == 3600:
        stats_dict['played_full'] = 1
    else:
        stats_dict['played_full'] = 0
    for stat in STATS_CONSIDERED:
        stats_dict['avg_' + stat] = df[stat].mean()
        stats_dict['sum_' + stat] = df[stat].sum()
    df = df[df['play_type'] == 'pass']
    stats_dict['QB'] = df['passer_player_name'].iloc[0]
    for stat in STATS_CONSIDERED:
        stats_dict['avg_pass_' + stat] = df[stat].mean()
        stats_dict['sum_pass_' + stat] = df[stat].sum()
    return stats_dict


def process_game_side(df_side):
    df_side = df_side[(df_side['two_point_attempt'] == 0) & (df_side['extra_point_attempt'] == 0)]
    qb_counts = df_side.groupby('passer_player_name').count()['game_id'].to_dict()
    # counts number of plays by each QB
    # 'game_id' chosen as a random column that will never be NaN for the count
    # note that NaN is automatically excluded as a level by groupby: https://stackoverflow.com/questions/18429491/pandas-groupby-columns-with-nan-missing-values
    rando_trick_QB = None
    if len(qb_counts) > 1:
        for qb, count in qb_counts.items():
            if count < 7:
                rando_trick_QB = qb
        if rando_trick_QB is not None:
            del qb_counts[rando_trick_QB]

    if len(qb_counts) > 2:
        return None, None # I don't want to deal with this
    elif len(qb_counts) == 2:
        prev_QB = df_side[df_side['play_type'] == 'pass']['passer_player_name'].iloc[0]
        change_times = []
        change_idx = []
        for i, tup in enumerate(df_side.itertuples()):
            if pd.isna(tup.passer_player_name):
                continue
            if tup.passer_player_name != prev_QB:
                change_times.append(tup.game_seconds_remaining)
                change_idx.append(i) # TODO: find the more pythonic way to do this
                prev_QB = tup.passer_player_name
        QB_change_time, QB_change_idx = change_times[0], change_idx[0]
        df_1st_qb = df_side.iloc[:QB_change_idx] # [df_side['play_type'] == 'pass']
        df_2nd_QB = df_side.iloc[QB_change_idx:]
        stats_main_QB = process_QB_play(df_1st_qb, 3600-QB_change_time)
        stats_2nd_QB = process_QB_play(df_2nd_QB, QB_change_time)
    else:
        if rando_trick_QB is not None:
            df_side = df_side[df_side['passer_player_name'] != rando_trick_QB]
        # catches instances where like, julian edelman throws one pass in the game
        stats_main_QB = process_QB_play(df_side, 3600)
        stats_2nd_QB = None
    return stats_main_QB, stats_2nd_QB

def process_game_df(df_game):
    home_team = df_game['home_team'].iloc[0]
    df_home = df_game[df_game['posteam'] == home_team]
    away_team = df_game['away_team'].iloc[0]
    df_away = df_game[df_game['posteam'] == away_team]
    stats_1st_QB_home, stats_2nd_QB_home = process_game_side(df_home)
    stats_1st_QB_away, stats_2nd_QB_away = process_game_side(df_away)
    final_home_score = df_game.iloc[-1]['total_home_score']
    final_away_score = df_game.iloc[-1]['total_away_score']
    if final_home_score > final_away_score:
        home_win = 1
    elif final_home_score < final_away_score:
        home_win = 0
    else:
        home_win = .5

    game_return = []
    for stats_qb in [stats_1st_QB_home, stats_2nd_QB_home, stats_1st_QB_away, stats_2nd_QB_away]:
        if stats_qb is None:
            continue
        if stats_qb['team'] == home_team:
            stats_qb['win'] = home_win
        else:
            stats_qb['win'] = 1 - home_win
        game_return.append(stats_qb)
    return game_return

def run_stats_on_team_season(df_t_stats, considered_stats, main_qb):
    stat_difs = {}
    stat_mains = {}
    stat_backups = {}
    for stat in considered_stats:
        #print(df_t_stats[['QB', 'played_full', stat]])
        df_main_QB_full = df_t_stats[(df_t_stats['QB'] == main_qb) & (df_t_stats['played_full'] == 1)]
        df_backup_QB_full = df_t_stats[(df_t_stats['QB'] != main_qb) & (df_t_stats['played_full'] == 1)]
        #df_mixed_QB_full = df_t_stats,[df_t_stats,['QB'] != main_qb | df_t_stats,['played_full'] == 0]
        stat_main_QB_full = df_main_QB_full[stat].mean()
        stat_backup_QB_full = df_backup_QB_full[stat].mean()
        stat_difs[stat] = stat_main_QB_full - stat_backup_QB_full
        stat_mains[stat] = stat_main_QB_full
        stat_backups[stat] = stat_backup_QB_full
        #print('main qb:', main_qb)
        #print('main:', stat_main_QB_full, 'backup:', stat_backup_QB_full, 'dif:', stat_difs[stat])
        #print()
    return stat_difs, stat_mains, stat_backups



def run_stats_all_teams(df_stats, considered_stats):
    teams = df_stats['team'].unique()
    print(df_stats[['season', 'team', 'QB']])
    df_team_groups = df_stats.groupby(['season', 'team']) # TODO: team, season
    difs_by_team_season = defaultdict(list)
    mains_by_team_season = defaultdict(list)
    backups_by_team_season = defaultdict(list)

    for team_season, df_team_stats in df_team_groups:
        qb_counts = df_team_stats.groupby('QB').count()['team'].to_dict()
        max_count = 0
        main_qb = None
        print(qb_counts)
        for qb, count in qb_counts.items():
            if count > max_count:
                main_qb = qb
                max_count = count
        stat_difs, stat_mains, stat_backups = run_stats_on_team_season(df_team_stats, considered_stats, main_qb)
        for stat, val in stat_difs.items():
            if not np.isnan(val):
                difs_by_team_season[stat].append(val)
                mains_by_team_season[stat].append(stat_mains[stat])
                backups_by_team_season[stat].append(stat_backups[stat])
    stats_print_tuples = []
    for stat, stat_difs in difs_by_team_season.items():
        difs_by_team_season[stat] = [val_dif for val_dif in stat_difs if val_dif is not None]
        mains_by_team_season[stat] = [main_dif for main_dif, val_dif in zip(mains_by_team_season[stat], stat_difs) if val_dif is not None]
        backups_by_team_season[stat] = [back_dif for back_dif, val_dif in zip(backups_by_team_season[stat], stat_difs) if val_dif is not None]

        dif_mean = quick_mean(difs_by_team_season[stat])
        dif_se = quick_se(difs_by_team_season[stat])
        dif_t = dif_mean / dif_se
        n = len(mains_by_team_season[stat])
        basic_d = dif_t / sqrt(n)
        try:
            dav = dif_mean / (stdev(mains_by_team_season[stat]) + stdev(backups_by_team_season[stat])) * 2
        except:
            print('Skipping:', stat)
            continue
        main_mean = quick_mean(mains_by_team_season[stat])
        backup_mean = quick_mean(backups_by_team_season[stat])
        print_str = 'Stat: {stat}, main = {main_mean:,.3g}, backup = {backup_mean:,.3g}, t = {t:+.1f}, d_basic = {d:+.2f}, dav = {dav:+.2f}, n = {n}'.\
            format(stat=stat, main_mean=main_mean, backup_mean=backup_mean, t=dif_t, d=basic_d, dav=dav, n=n)
        if not np.isnan(dif_t):
            stats_print_tuples.append((dif_t, print_str))
    stats_print_tuples.sort(key=lambda x:abs(x[0]))
    prev_t = 0
    for stat, print_str in stats_print_tuples:
        if int(abs(stat)) > prev_t:
            if int(abs(stat)) == 2:
                color = Fore.RED # p < .05 threshold is important
            else:
                color = Fore.GREEN # otherwise just indicate every t-threshold in increments of 1
            prev_t = int(abs(stat))
        else:
            color = Fore.RESET
        if 'win' in print_str:
            color = Fore.MAGENTA
        print(color, print_str)

        #print('Stat:', stat, 'main =', main_mean, 'backup =', backup_mean, 't =', dif_t, 'n =', len(difs_by_team_season[stat]))

def quick_mean(l):
    return sum(l) / len(l)

def quick_se(l):
    return np.std(l) / sqrt(len(l))

def get_season_from_date(date):
    date_split = date.split('/')
    if int(date_split[0]) < 3:
        return int(date_split[2]) - 1 # returns the year minus 1
    else:
        return int(date_split[2]) # returns the year

def load_df():
    df = pd.read_csv('pbp_2009_2018.csv')
    df.dropna(subset=['game_date'], inplace=True)
    df['season'] = df['game_date'].apply(get_season_from_date)
    strip_unnecessary_columns(df)
    return df

def prepare_df_stats(df):
    df = df[df['season'] < 2019]
    df_game_groups = df.groupby('game_id')
    all_games_stats = []
    for game_id, df_game in df_game_groups:
        all_games_stats.extend(process_game_df(df_game))
    df_stats = pd.DataFrame(all_games_stats)
    return df_stats

def pickle_wrap(filename, callback,easy_override=False):
    import os
    if os.path.isfile(filename) and not easy_override:
        print('Loading...')
        with open(filename, "rb") as file:
            pk = pickle.load(file)
            return pk
    else:
        output = callback()
        with open(filename, "wb") as new_file:
            pickle.dump(output, new_file)
        return output


if __name__ == '__main__':
    easy_override = True
    df = pickle_wrap('pbp.pkl', load_df, easy_override=easy_override)
    df_stats = pickle_wrap('df_stats.pkl', lambda: prepare_df_stats(df), easy_override=easy_override)
    stats_considered_product = product(['sum_', 'avg_', 'sum_pass_', 'avg_pass_'], STATS_CONSIDERED)
    stats_considered_product = list(map(''.join, stats_considered_product))
    #stats_considered_product = ['sum_pass_yards_gained']
    run_stats_all_teams(df_stats, stats_considered_product + ['win'])



