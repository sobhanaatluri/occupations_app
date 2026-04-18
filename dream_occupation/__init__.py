from otree.api import *
import csv
from sklearn.metrics.pairwise import cosine_similarity
import os
import pandas as pd
import openai
import numpy as np
import random
import time
#from memory_profiler import profile

import sys

# Now, you can import from utils
from utils.openai_utils import set_openai_key
from utils.utils import load_embeddings

# Get the directory of the current script (__init__.py)
current_app_dir = os.path.dirname(os.path.abspath(__file__))

# Move one level up to `representations_nova`
parent_dir = os.path.dirname(current_app_dir)

# Add `representations_nova` to sys.path if not already added
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


doc = """
Your app description
"""

#@profile
def load_job_data(filepath):
    

    # Get the directory of the current script (__init__.py)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    print("load_job_data()")
    print(os.getcwd())
    # Construct the absolute path to the CSV file
    csv_file_path = os.path.join(current_script_dir, filepath)
    
    df = pd.read_csv(csv_file_path)
    
    return df

class C(BaseConstants):
    NAME_IN_URL = 'dream_occupation'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3  # Allowing up to 3 retries
    #embed_path = "all_embed.csv"
    job_path = "job_match.csv"
    job_title_embeddings = load_embeddings(os.path.join(parent_dir, "_static/all_embed2.csv"))
    job_df = load_job_data(job_path)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


#@profile  
def generate_embeddings(texts, batch_size = 2000):
    
    set_openai_key()  # Ensure API key is set
    
    if len(texts)>2000:
        
        response_list = []
        n = len(texts) // batch_size + bool(len(texts) % batch_size)
        for i in range(n):
            #print(i)
            begin = i*2000
            end = min(len(texts), (i+1)*2000)
            
            try:
                response = openai.Embedding.create(
                  input=texts[begin:end],
                  engine="text-embedding-ada-002")
            except:
                time.sleep(10)
                response = openai.Embedding.create(
                  input=texts[begin:end],
                  engine="text-embedding-ada-002")
            
            
            #reponse_list.append(response) 
            response_list.append(embedding['embedding'] for embedding in response['data'])
            
        response_l = [element for nestedlist in response_list for element in nestedlist]
        
        return response_l
    else:
        response = openai.Embedding.create(
        input=texts,
        engine="text-embedding-ada-002"
        )
        return [embedding['embedding'] for embedding in response['data']]
    
# Function to find top N closest matches
def find_top_matches(query_embedding, candidate_embeddings, n=3):
    
    similarities = cosine_similarity([query_embedding], candidate_embeddings)[0]
    indices = similarities.argsort()[::-1]
    
    #job_path = "/Users/sobhanaatluri/Dropbox/00-Stanford-MacroOB/02-Research Projects/Schemas/Data/Intermediate/job_match.csv"
        
    #job_df = pd.read_csv(job_path)
    selected_jobs = C.job_df.iloc[indices][['Occupation', 'Job Family']].drop_duplicates(subset=['Occupation'])
    top_indices = selected_jobs.index[:n]
        
    return top_indices

def start_backend_process(player, respondent_job_title):

    respondent_embedding = generate_embeddings([respondent_job_title])[0]
    
    #-------------- FOR PRODUCTION -----------------#
    top_match_indices = find_top_matches(respondent_embedding, C.job_title_embeddings, n=5)
    
    #-------------- FOR TESTING -----------------#
    #top_match_indices = find_top_matches(respondent_embedding, C.job_title_embeddings, n=5)

    indices_str = '+'.join(map(str, top_match_indices))
    
    return indices_str
    

class Player(BasePlayer):

    
    dream_occupation = models.StringField(
        label='Imagine there were no barriers, no limits—no need to retrain, relocate, or worry about money. What’s a dream job you’d love to do?'
    )
    
    selected_dream_job = models.StringField(
        label="Select the closest match to your dream occupation"
    )
    
    top_match_indices_dream = models.StringField()
    
    valid_choice = models.BooleanField(initial=False)

    
    # closest matches by activity and skill vectors in O*Net to the matched O*Net job provided by respondent
    closest_matches = models.StringField()


# Pages

class EndPage(Page):
    
    @staticmethod
    def is_displayed(player):

        if player.round_number == 1:
            return False
        else:
            return False

class DreamOccupation(Page):
    
    form_model = 'player'
    form_fields = ['dream_occupation']
    
    @staticmethod
    def is_displayed(player):
        
        condition0 = player.round_number == 1 
        
        if condition0:
            condition1 = True
            condition2 = False
        else:
            #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            #print(player.in_round(player.round_number - 1).selected_job)
            condition1 = False
            condition2 = False
            if player.participant.vars['valid_choice'] == False:
                condition2 = player.in_round(player.round_number - 1).selected_dream_job == "None of the above are close"
        #return player.consent == 'AGREE'
        #return player.round_number == 1 or player.in_round(player.round_number - 1).selected_job == "None of the above are close"
        
        return condition1 or condition2
    
    def vars_for_template(player: Player):
    
        turns_left = {
            1: 'two',
            2: 'one'
        }
        
        if player.round_number !=3:
            
            if player.round_number ==2:
                custom_text = "If you don't see a good match, you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more time."
                
            else:
                custom_text = "If you don't see a good match, you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more times."
        else:
            custom_text = "If you don't see a good match, select the closest occupation."

        return {
            'custom_text': custom_text
        }
    
    def error_message(player, values):
        
        if values['dream_occupation']=='':
            return 'Please enter a valid occupation.'
    
    def before_next_page(player, timeout_happened):
        
        # Get user's input
        respondent_job_title = player.dream_occupation
        player.top_match_indices_dream = start_backend_process(player, respondent_job_title)

        
class DreamOccupationSelection(Page):
    
    form_model = 'player'
    form_fields = ['selected_dream_job']
    
    @staticmethod
    def is_displayed(player):
        
        if player.round_number == 1:
            return True
        else:
            if player.participant.vars['valid_choice'] == False:
                return player.in_round(player.round_number - 1).selected_dream_job == "None of the above are close"
            else:
                return False
    
    def vars_for_template(player: Player):
        
        closest_indices = list(map(int, player.top_match_indices_dream.split('+')))
        
        # Load the jobs dataset
        #job_path = "/Users/sobhanaatluri/Dropbox/00-Stanford-MacroOB/02-Research Projects/Schemas/Data/Intermediate/job_match.csv"
        
        #job_df = load_job_data(job_path)
        selected_jobs = C.job_df.loc[closest_indices][['Occupation', 'Job Family']].drop_duplicates(subset=['Occupation'])  # Adjust the column name as needed

        job_options = selected_jobs['Occupation'].to_list()
        job_options = sorted(job_options, key=lambda x: random.random())

        if player.round_number !=3:
            job_options.append("None of the above are close")
        
        turns_left = {
            1: 'two',
            2: 'one'
        }
        
        if player.round_number ==1:
            custom_text1 = "'None of the above are close'"
            custom_text = "and you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more times."
        elif player.round_number ==2:
            custom_text1 = "'None of the above are close'"
            custom_text = "and you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more time."
        else:
            custom_text1 = "the next closest option."
            custom_text = ""
        
        return dict(job_options=job_options,
                    custom_text = custom_text,
                   custom_text1 = custom_text1)
    
    def before_next_page(player: Player, timeout_happened):
        
        if player.selected_dream_job != 'None of the above are close':
            player.participant.vars['valid_choice'] = True
        else:
            player.participant.vars['valid_choice'] = False
        
        player.participant.vars['dream_job'] = player.selected_dream_job
        #print(type(C.job_title_embeddings))
        
    def error_message(player, values):
        
        #print('value is not :', values['selected_job']=='')
        if values['selected_dream_job']=='':
            return 'Please select an option.'

        
page_sequence = [DreamOccupation, DreamOccupationSelection]
