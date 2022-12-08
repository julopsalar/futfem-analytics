import time
import pandas as pd
import numpy as np

"""

"""

def calculate_xpoints(matches, num_simulations=20000, debug=False):

    home_xp = []
    away_xp = []
    # For each match, apply the Montecarlo Simulation to get xPoints for both teams
    for idx, m in matches.iterrows():
        if (m['xGHome'] != '') & (m['xGAway'] != ''):
            home, away, xGHome, xGAway = m['Home'], m['Away'], float(m['xGHome']), float(m['xGAway'])
        else:
            home_xp.append(0)
            away_xp.append(0)
            continue
    
        if debug:
            print(f'Processing match #{idx}: \
                    {home} ({xGHome}) vs ({xGAway}) {away}')
        # Auxiliar Variables
        count_home_wins = 0
        count_home_loss = 0
        count_away_wins = 0
        count_away_loss = 0
        count_draws = 0
        tot_sim_time = 0
        # Run the n simulations
        for i in range(num_simulations):
            # get simulation start time
            start_time = time.time()
            # run the sim - generate a random Poisson distribution
            target_home_goals_scored = np.random.poisson(xGHome)
            target_away_goals_scored = np.random.poisson(xGAway)
            # if more goals for home team => home team wins
            if target_home_goals_scored > target_away_goals_scored:
                count_home_wins += 1
                count_away_loss += 1
            # if more goals for away team => away team wins
            elif target_home_goals_scored < target_away_goals_scored:
                count_away_wins += 1
                count_home_loss += 1
            elif target_home_goals_scored == target_away_goals_scored:
                count_draws += 1

            # get end time
            end_time = time.time()
            # add the time to the total simulation time
            tot_sim_time += round((end_time - start_time), 5)

        # Calculate probabilities
        home_win_probability = round((count_home_wins/num_simulations), 4)
        away_win_probability = round((count_away_wins/num_simulations), 4)
        draw_probability = round((count_draws/num_simulations), 4)
        
        xp_h = round(home_win_probability*3+draw_probability, 2)
        home_xp.append(xp_h)

        xp_a = round(away_win_probability*3+draw_probability, 2)
        away_xp.append(xp_a)

        if debug:
            print('Simulation completed in ', round(tot_sim_time, 2), ' seconds')
            print(f'{100*home_win_probability}% ({xp_h}xP) -- {round(100*draw_probability, 2)}% \
                    -- {100*away_win_probability} ({xp_a}xP)')

    return home_xp, away_xp