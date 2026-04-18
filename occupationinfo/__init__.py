from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'occupationinfo'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    
    num_years = models.StringField(
        label='How long have you been in this role (number of years using digits)?',
        blank=True  # Allows this field to be empty
    )
    
    skills = models.StringField(
        label='What are some of the main skills you use on the job?',
        blank=True  # Allows this field to be empty
    )
    
    tasks = models.StringField(
        label='What are some of primary job duties you perform on the job?',
        blank=True  # Allows this field to be empty
    )


# PAGES
class OccupationInfo(Page):
    
    form_model = 'player'
    form_fields = ['num_years', 'skills', 'tasks']
    
    @staticmethod
    def is_displayed(player):
        return True
        #return player.participant.vars['consent'] == 'AGREE'


page_sequence = [OccupationInfo]
