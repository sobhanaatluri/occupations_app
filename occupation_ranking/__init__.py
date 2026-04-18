from otree.api import *
import pandas as pd
import random
import os

doc = """
Your app description
"""

class C(BaseConstants):
    NAME_IN_URL = 'occupation_ranking'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    #occupations = ['Talent Directors', 'Human Resources Assistants, Except Payroll and Timekeeping', 'Credit Authorizers, Checkers, and Clerks', 'Models', 'Exercise Trainers and Group Fitness Instructors', 'Hosts and Hostesses, Restaurant, Lounge, and Coffee Shop', 'Choreographers', 'Art, Drama, and Music Teachers, Postsecondary', 'Music Directors and Composers']
    targets_path = "target_jobs_skwa.csv"
    targets = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/"+targets_path)

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    occupations_order = models.StringField()

# PAGES
class OccupationRankingPage(Page):
    form_model = 'player'
    form_fields = ['occupations_order']

    def is_displayed(self):
        return True

    def vars_for_template(player):
        
        #--------- FOR PRODUCTION-------------#
        focal_job = player.participant.vars['onet_job']
        
        #--------- FOR TESTING-------------#
        #focal_job = 'Actors'#"Dentists, General"#"Actors"
        
        #print(len(C.targets['focal_job'].unique()))
        
        # Filter for the focal job
        target_jobs = C.targets[C.targets['focal_job'] == focal_job]
        #print(target_jobs)
        # To get just the list of target job names:
        target_job_list = target_jobs['target_job'].tolist()
        
        # Shuffle the list (in-place)
        random.shuffle(target_job_list)
        
        #print("Target job list:", target_job_list)
        
        return {
            #'occupations': Constants.occupations,
            'occupations': target_job_list,
            'focal_job': focal_job
        }
    
    def before_next_page(player, timeout_happened):
        
        player.participant.vars['occupations_order'] = player.occupations_order
        #print('Occupations Order')
        #print(player.occupations_order)

page_sequence = [OccupationRankingPage]