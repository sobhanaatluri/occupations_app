from otree.api import *

doc = """
Job Transition Survey
"""

class C(BaseConstants):
    NAME_IN_URL = 'job_transition'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # First page questions
    transition_consideration = models.StringField(
        choices=['Changing careers', 'Changing jobs within the same domain', 'Neither', 'Other'],
        label='Have you been thinking about transitioning or changing jobs?',
        widget=widgets.RadioSelect
    )
    
    transition_other = models.StringField(
        label='If "Other", please specify:',
        blank=True
    )
    
    transition_timeframe = models.StringField(
        choices=['Not thinking about it', 'Last 6 months', 'Last 12 months', 'More than a year'],
        label='Since when have you been considering a transition?',
        widget=widgets.RadioSelect
    )
    
    # Second page question
    transition_hopes_concerns = models.LongStringField(
        label='What are your hopes and concerns about the job move? Please provide your top two hopes and top two concerns.',
    )

# PAGES
class TransitionQuestions(Page):
    form_model = 'player'
    form_fields = ['transition_consideration', 'transition_other', 'transition_timeframe']
    
    @staticmethod
    def is_displayed(player):
        return True

class HopesConcerns(Page):
    form_model = 'player'
    form_fields = ['transition_hopes_concerns']
    
    @staticmethod
    def is_displayed(player):
        return True

page_sequence = [TransitionQuestions, HopesConcerns]