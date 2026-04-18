from otree.api import *

doc = """
This app allows participants to rank 6 values according to their preferences.
"""

class C(BaseConstants):
    NAME_IN_URL = 'values_ranking'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    values = [
        'Achievement', 'Independence', 'Recognition',
        'Relationships', 'Support', 'Working Conditions'
    ]
    values_descriptions = {
        'Achievement': "Results oriented, allows use of strongest abilities.",
        'Independence': "Work on own, make decisions.",
        'Recognition': "Offers advancement and leadership opportunities.",
        'Relationships': "Service to others, friendly non-competitive environment.",
        'Support': "Supportive management, strong backing.",
        'Working Conditions': "Job security, good conditions."
    }

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    values_order = models.StringField()

class ValuesRankingPage(Page):
    form_model = 'player'
    form_fields = ['values_order']

    def vars_for_template(self):
        return {
            'values': C.values,
            'values_descriptions': C.values_descriptions
        }
    
    def before_next_page(player, timeout_happened):

        player.participant.vars['values_order'] = player.values_order
        #print('Values Order')
        #print(player.values_order)

page_sequence = [ValuesRankingPage]