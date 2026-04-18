from otree.api import *
import csv
import os
import pandas as pd
import numpy as np
from collections import defaultdict
import random
#from memory_profiler import profile

doc = """
Your app description
"""

#@profile
def shuffle_pairs(x, left_col, right_col):
    
    '''
    Function to randomize the sequence of pairs presented to the participant and 
    randomize which job appears on the left or right side, 
    ensuring that repeating job titles alternate between the left and right positions 
    while preserving the original pairings.
    '''
    x=x.sample(frac = 1).reset_index(drop = True)
    
    #title_counts = x[left_col].append(x[right_col]).value_counts()
    title_counts = pd.concat([x[left_col], x[right_col]]).value_counts()
    repeating_titles = title_counts[title_counts > 1].index
    last_position = defaultdict(lambda: 'right')

    randomized_pairs = []

    for index, row in x.iterrows():
        left_title, right_title, focal_job = row[left_col], row[right_col], row['focal_job']

        # Decide whether to swap based on repeating title positions
        if left_title in repeating_titles or right_title in repeating_titles:
            swap = False
            swapback = False
            if left_title in repeating_titles:
                swap = (last_position[left_title] == 'left')
                last_position[left_title] = 'right' if swap else 'left'
            if right_title in repeating_titles:
                swap = (last_position[right_title] == 'right')
                last_position[right_title] = 'left' if swap else 'right'

            if swap:
                randomized_pairs.append((right_title, left_title, focal_job))
            else:
                randomized_pairs.append((left_title, right_title, focal_job))
                
            if left_title in repeating_titles and right_title in repeating_titles:
                if randomized_pairs[index-1][0] == randomized_pairs[index][0] or randomized_pairs[index-1][1] == randomized_pairs[index][1]:
                    if swap:
                        randomized_pairs[index] = (left_title, right_title, focal_job)
                    else:
                        randomized_pairs[index] = (right_title, left_title, focal_job)
        else:
            # Randomly swap non-repeating titles
            if random.choice([True, False]):
                randomized_pairs.append((right_title, left_title, focal_job))
            else:
                randomized_pairs.append((left_title, right_title, focal_job))
                
    return pd.DataFrame(randomized_pairs, columns =['target_job_1', 'target_job_2', 'focal_job'])

#@profile
def load_dist_data(filepath):
    

    # Get the directory of the current script (__init__.py)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    print("load_dist_data()")
    print(os.getcwd())
    # Construct the absolute path to the CSV file
    csv_file_path = os.path.join(current_script_dir, filepath)
    
    df = pd.read_csv(csv_file_path)
    
    return df
    
    
def find_hierarchy(target_job1, target_job2, choice, onet_job, player):
    
    """
    Analyzes user choices between two target jobs for a given focal job and computes 
    whether the choices align with smaller distances in skills, knowledge, and work activities.

    Parameters:
    target_job1 : A list of job titles presented in position 1 in the ranking task.
    target_job2 : A list of job titles presented in position 2 in the ranking task.
    choice : A list of integers (1 or 2), indicating which job the user selected in each trial.
    onet_job : The focal job that the user is comparing the target jobs against.
    player : The current player instance in the oTree experiment, used to access participant variables.

    Returns:
    choice_counts : A dictionary containing counts of how many times the chosen job was closer to the focal job 
        on each dimension:
        - 'skills_closer': Number of times the choice had a smaller skill distance.
        - 'knowledge_closer': Number of times the choice had a smaller knowledge distance.
        - 'activities_closer': Number of times the choice had a smaller work activity distance.

    Notes:
    - The function assumes that `C.dist_df` contains the necessary job similarity distances 
      with the columns: ['focal_job', 'target_job', 'key', 'dist_s_i_c', 'dist_wa_i_c', 'dist_k_i_c', 'dist_a_i_c'].
    - The function only operates on rows where `focal_job` matches the `onet_job` from participant vars.
    - The calculation is performed for each trial, and the results are aggregated.
    """
    
    # Load job data specific to the player's focal job
    #job_df = C.dist_df[C.dist_df['focal_job'] == player.participant.vars['onet_job']].reset_index(drop=True)
    job_df = C.dist_df[C.dist_df['focal_job'] == onet_job].reset_index(drop=True)
    
    # Split target jobs by "+"
    target_job1 = target_job1.split("+")
    target_job2 = target_job2.split("+")

    # Split choices by "," and convert to integers
    choice = list(map(int, choice.strip("[]").split(",")))
    
    #print([onet_job] * len(target_job1))
    #print(target_job1)
    #print(target_job2)
    #print(choice)
    #print(len([t1 if c == 1 else t2 for t1, t2, c in zip(target_job1, target_job2, choice)]))
    
    # Create a DataFrame to store the hierarchy comparison results
    hierarchy_df = pd.DataFrame({
        'focal_job': [onet_job] * len(target_job1),
        'target_job1': target_job1,
        'target_job2': target_job2,
        'choice': choice,
        'choice_value': [t1 if c == '1' else t2 for t1, t2, c in zip(target_job1, target_job2, choice)]
    })

    # Function to extract distances from job_df
    def get_distances(target_job):
        match = job_df[job_df['target_job'] == target_job]
        if not match.empty:
            return match.iloc[0][['dist_s_i_c', 'dist_k_i_c', 'dist_wa_i_c']].values
        return [None, None, None]

    # Retrieve distances for target jobs
    hierarchy_df[['dist_s_1', 'dist_k_1', 'dist_wa_1']] = hierarchy_df['target_job1'].apply(lambda x: pd.Series(get_distances(x)))
    hierarchy_df[['dist_s_2', 'dist_k_2', 'dist_wa_2']] = hierarchy_df['target_job2'].apply(lambda x: pd.Series(get_distances(x)))

    # Count choices based on distances being smaller for target_job1 or target_job2
    hierarchy_df['chosen_closer_s'] = (hierarchy_df['dist_s_1'] < hierarchy_df['dist_s_2']) & (hierarchy_df['choice'] == 1) | \
                                      (hierarchy_df['dist_s_2'] < hierarchy_df['dist_s_1']) & (hierarchy_df['choice'] == 2)
    
    hierarchy_df['chosen_closer_k'] = (hierarchy_df['dist_k_1'] < hierarchy_df['dist_k_2']) & (hierarchy_df['choice'] == 1) | \
                                      (hierarchy_df['dist_k_2'] < hierarchy_df['dist_k_1']) & (hierarchy_df['choice'] == 2)
    
    hierarchy_df['chosen_closer_wa'] = (hierarchy_df['dist_wa_1'] < hierarchy_df['dist_wa_2']) & (hierarchy_df['choice'] == 1) |\
                                       (hierarchy_df['dist_wa_2'] < hierarchy_df['dist_wa_1']) & (hierarchy_df['choice'] == 2)

    # Calculate summary counts
    summary_counts = {
        'closer_on_skills': hierarchy_df['chosen_closer_s'].sum(),
        'closer_on_knowledge': hierarchy_df['chosen_closer_k'].sum(),
        'closer_on_activities': hierarchy_df['chosen_closer_wa'].sum()
    }
    #print(summary_counts)

    return summary_counts
    
    
class C(BaseConstants):
    NAME_IN_URL = 'representations_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    print(os.path.dirname(os.path.abspath(__file__)))
    print("***********************representations_task**************************************")
    pairs_path = "triplets_30_s_wa.csv"
    #pairs = pd.read_csv(pairs_path)
    pairs = pd.read_csv("representations_task_s_wa/triplets_30_s_wa.csv")
    dist_path = 'master_dist_skwa.csv'
    dist_df = load_dist_data(dist_path)
    

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    
    onet_job = models.StringField()
    target_job1 = models.StringField()
    target_job2 = models.StringField()
    focal_job = models.StringField()
    choice = models.StringField()
    time = models.StringField()
    s_count_task1 = models.IntegerField()
    wa_count_task1 = models.IntegerField()
    k_count_task1 = models.IntegerField()


# PAGES

class InstructionsPage(Page):
    
    # This function checks if the page should be shown
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
    def vars_for_template(player):
        
        job = player.participant.vars['onet_job']
        #job = job = "Floral Designers" # for testing

        return dict(focal_job = job)

## Selecting among job Pairs ##
class ChoicePage(Page):
    
    form_model = 'player'
    form_fields = ['choice', 'time', 'target_job1', 'target_job2']
    
    def vars_for_template(player):
        
        
        job = player.participant.vars['onet_job']
        #job = "Floral Designers" # for testing
        cols = ['focal_job', 'target_job_s', 'target_job_wa']
        #cols = ['focal_job', 'target_job_k', 'target_job_wa']
        #cols = ['focal_job', 'target_job_k', 'target_job_s']
        
        pairs = C.pairs.loc[C.pairs['title']==job, cols]
        pairs = shuffle_pairs(pairs,'target_job_s', 'target_job_wa')
        #pairs = shuffle_pairs(pairs,'target_job_k', 'target_job_wa')
        #pairs = shuffle_pairs(pairs,'target_job_k', 'target_job_s')
        #pairs = pairs.iloc[0:5,] # for testing
        
        focal_job = pairs['focal_job'].to_list()
        target_job_1 = pairs['target_job_1'].to_list()
        target_job_2 = pairs['target_job_2'].to_list()
        
        # Save the concatenated string to the participant's vars
        #player.participant.vars['focal_job'] = "*".join([str(item) for item in focal_job]) #focal_job 
        #player.participant.vars['target_job_1'] = "*".join([str(item) for item in target_job_1]) #target_job_1
        #player.participant.vars['target_job_2'] = "*".join([str(item) for item in target_job_2]) #target_job_2

        return dict(focal_job = focal_job, target_job_1=target_job_1, target_job_2=target_job_2)
    
    def before_next_page(player, timeout_happened):

        player.participant.vars['choice'] = player.choice
        
        summary_counts = find_hierarchy(player.target_job1, player.target_job2, player.choice, player.participant.vars['onet_job'], player)
        #player.participant.vars['onet_job'] = "Floral Designers"
        player.participant.vars['s_count_task1'] = int(summary_counts['closer_on_skills'])
        player.participant.vars['k_count_task1'] = int(summary_counts['closer_on_knowledge'])
        player.participant.vars['wa_count_task1'] = int(summary_counts['closer_on_activities'])
        
        #player.onet_job = "Floral Designers"
        player.s_count_task1 = int(summary_counts['closer_on_skills'])
        player.k_count_task1 = int(summary_counts['closer_on_knowledge'])
        player.wa_count_task1 = int(summary_counts['closer_on_activities'])


page_sequence = [InstructionsPage, ChoicePage]
