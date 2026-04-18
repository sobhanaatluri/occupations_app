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
    print("load_job_data() - representations_v2")
    
    # Construct the absolute path to the CSV file
    csv_file_path = os.path.join(current_script_dir, filepath)
    
    df = pd.read_csv(csv_file_path)
    
    return df

class C(BaseConstants):
    NAME_IN_URL = 'representations_v2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5  # Allowing up to 5 retries
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
    selected_jobs = C.job_df.iloc[indices][['Occupation', 'Job Family']].drop_duplicates(subset=['Occupation'])
    top_indices = selected_jobs.index[:n]
        
    return top_indices

def start_backend_process(respondent_job_title):
    #embed_path = "/Users/sobhanaatluri/Dropbox/00-Stanford-MacroOB/02-Research Projects/Schemas/Data/Intermediate/all_embed.csv"
 
    #embed_path = "https://drive.google.com/file/d/1jlPxuS8h3-05Xxq3CyPeEQ3_GpPslTEK/view?usp=drive_link"

    #print(self.player.job_current)
    respondent_embedding = generate_embeddings([respondent_job_title.lower()])[0]
    top_match_indices = find_top_matches(respondent_embedding, C.job_title_embeddings, n=5)

    indices_str = '+'.join(map(str, top_match_indices))
    
    return indices_str
    

class Player(BasePlayer):
    
    consent = models.StringField(
        choices=['AGREE', 
                 'DISAGREE'],
        label="",
        widget=widgets.RadioSelect
    )
    
    prolific_id = models.StringField(default=str(""))
    

    job_current = models.StringField(
        label='What is your current or most recent role?',
        blank=True  # Allows this field to be empty
    )
    
    # closest title matches in O*Net to the title provided by respondent
    top_match_indices = models.StringField()
    
    selected_job = models.StringField(
        label="Select the most suitable job from the list below"
    )
    
    valid_choice = models.BooleanField(initial=False)

    
    # closest matches by activity and skill vectors in O*Net to the matched O*Net job provided by respondent
    closest_matches = models.StringField()


# Pages
class Consent(Page):
    
    form_model = 'player'
    form_fields = ['consent']
    
    def before_next_page(player, timeout_happened):

        player.participant.vars['consent'] = player.consent
        
    def is_displayed(player):
        return player.round_number == 1
    
    def error_message(player, values):
        
        if values['consent']=='':
            return 'Please select an option.'

class EndPage(Page):
    
    @staticmethod
    def is_displayed(player):

        if player.round_number == 1:
            return player.consent == 'DISAGREE'
        else:
            return False

class EmailCollection(Page):
    
    form_model = 'player'
    form_fields = ['email']
    
    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return player.consent == 'DISAGREE'
        else:
            return False
    
    @staticmethod
    def error_message(player, values):
        # Basic email validation
        if '@' not in values['email'] or '.' not in values['email']:
            return {'email': 'Please enter a valid email address'}
    

class InstructionsPage(Page):
    
    @staticmethod
    def is_displayed(player):
        
        if player.round_number == 1:
            return player.consent == 'AGREE'
        else:
            return False
        
        #return player.consent == 'AGREE' and player.round_number == 1
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.prolific_id = player.participant.label

class CurrentOccupation(Page):
    
    form_model = 'player'
    form_fields = ['job_current']
    
    @staticmethod
    def is_displayed(player):
        
        condition0 = player.round_number == 1 
        
        if condition0:
            condition1 = player.consent == 'AGREE'
            condition2 = False
        else:
            #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            #print(player.in_round(player.round_number - 1).selected_job)
            condition1 = False
            condition2 = False
            if player.participant.vars['valid_choice'] == False:
                condition2 = player.in_round(player.round_number - 1).selected_job == "None of the above are close"
        #return player.consent == 'AGREE'
        #return player.round_number == 1 or player.in_round(player.round_number - 1).selected_job == "None of the above are close"
        
        return condition1 or condition2
    
    def vars_for_template(player: Player):
    
        turns_left = {
            1: 'four',
            2: 'three',
            3: 'two',
            4: 'one',
        }
        
        if player.round_number !=5:
            
            if player.round_number ==4:
                custom_text = "If you don't see a good match, you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more time."
                
            else:
                custom_text = "If you don't see a good match, you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more times."
        else:
            custom_text = "If you don't see a good match, select the closest occupation."
        
        # if player.round_number == 1:
        #     custom_text = "If you don't see a good match, you can try submitting an alternate title for your role two more times."
        # elif player.round_number == 2:
        #     custom_text = "If you don't see a good match, you can try submitting an alternate title for your role one more time."
        # else:
        #     custom_text = "If you don't see a good match, select the closest occupation."

        # Return the customized text to the template
        return {
            'custom_text': custom_text
        }
    
    def error_message(player, values):
        
        if values['job_current']=='':
            return 'Please enter a valid occupation.'
    
    def before_next_page(player, timeout_happened):
        
        # Get user's input
        player.prolific_id = player.participant.label # remove if needed
        respondent_job_title = player.job_current
        player.top_match_indices = start_backend_process(respondent_job_title)

        
class OccupationSelection(Page):
    
    form_model = 'player'
    form_fields = ['selected_job']
    
    @staticmethod
    def is_displayed(player):
        
        if player.round_number == 1:
            return player.consent == 'AGREE'
        else:
            if player.participant.vars['valid_choice'] == False:
                return player.in_round(player.round_number - 1).selected_job == "None of the above are close"
            else:
                return False
    
    def vars_for_template(player: Player):
        
        closest_indices = list(map(int, player.top_match_indices.split('+')))
        #print(len(closest_indices))
        #print(C.job_df.loc[closest_indices][['Occupation', 'Job Family']])
        selected_jobs = C.job_df.loc[closest_indices][['Occupation', 'Job Family']].drop_duplicates(subset=['Occupation'])  # Adjust the column name as needed
        #selected_jobs = C.job_df.loc[closest_indices][['title', 'Job Family']]  # Adjust the column name as needed

        job_options = selected_jobs['Occupation'].to_list()
        #job_options = selected_jobs['title'].to_list()
        job_options = sorted(job_options, key=lambda x: random.random())

        if player.round_number !=5:
            job_options.append("None of the above are close")
        
        turns_left = {
            1: 'four',
            2: 'three',
            3: 'two',
            4: 'one',
        }
        
        if player.round_number !=5:
            custom_text1 = "'None of the above are close'"
            custom_text = "and you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more times."
        elif player.round_number ==4:
            custom_text1 = "'None of the above are close'"
            custom_text = "and you can try submitting an alternate title for your role "+ turns_left[player.round_number] +" more time."
        else:
            custom_text1 = "the next closest option."
            custom_text = ""
        
        # if player.round_number == 1:
        #     custom_text1 = "'None of the above are close'"
        #     custom_text = "and you can try submitting an alternate title for your role two more times."
        # elif player.round_number == 2:
        #     custom_text1 = "'None of the above are close'"
        #     custom_text = "and you can try submitting an alternate title for your role one more time."
        # else:
        #     custom_text1 = "the next closest option."
        #     custom_text = ""
        
        return dict(job_options=job_options,
                    custom_text = custom_text,
                   custom_text1 = custom_text1)
    
    def before_next_page(player: Player, timeout_happened):
        
        if player.selected_job != 'None of the above are close':
            player.participant.vars['valid_choice'] = True
        else:
            player.participant.vars['valid_choice'] = False
        
        player.participant.vars['onet_job'] = player.selected_job
        #print(type(C.job_title_embeddings))
        #player.participant.vars['all_embeddings'] = C.job_title_embeddings.copy()
        #print(type(player.participant.vars['all_embeddings']))
        #print(player.participant.vars['all_embeddings'][0])
        
    def error_message(player, values):
        
        #print('value is not :', values['selected_job']=='')
        if values['selected_job']=='':
            return 'Please select an option.'

        
page_sequence = [Consent, InstructionsPage, CurrentOccupation, OccupationSelection, EmailCollection, EndPage]
