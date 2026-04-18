from otree.api import *
import random

doc = """
App that handles the ranking of occupational attributes for the representations study.
This app contains the ranking pages that were previously in the representations_q app.
"""

class C(BaseConstants):
    NAME_IN_URL = 'similarity_transition_ranking'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Fields for storing the ranking responses
    similarity_order = models.StringField(
        blank=True,
        doc="Comma-separated ordered list of similarity factors"
    )
    
    transition_order = models.StringField(
        blank=True,
        doc="Comma-separated ordered list of transition factors"
    )
    
    # Optional fields for additional ranking data if needed
    similarity_list = models.StringField(blank=True)
    transition_list = models.StringField(blank=True)


# PAGES
class RankingPageA(Page):
    """
    Page for ranking similarity factors.
    """
    form_model = 'player'
    form_fields = ['similarity_order']

    def vars_for_template(player):
        similarity_options = [
            'Skills',
            'Tasks',
            'Knowledge',
            'Work Environment',
            'Education and Training',
            'Personal Values',
            'Industry/Sector'
        ]
        random.shuffle(similarity_options)

        # Store the shuffled list in participant vars for later use
        player.participant.vars['similarity_list'] = similarity_options

        return {
            'ranking_options': similarity_options  # Pass to the template
        }
    
    def before_next_page(player, timeout_happened):
        # Store the ranking in participant vars so it's accessible in other apps
        player.participant.vars['similarity_order'] = player.similarity_order


class RankingPageB(Page):
    """
    Page for ranking transition factors.
    """
    form_model = 'player'
    form_fields = ['transition_order']

    def vars_for_template(player):
        transition_options = [
            'Annual income',
            'Work-life balance',
            'Company culture',
            'Career growth opportunities',
            'Geographic location', 
            'Educational Requirements',
            'Skill Overlap', 
            'Task Overlap',
            'Social Status'
        ]
        random.shuffle(transition_options)

        # Store the shuffled list in participant vars for later use
        player.participant.vars['transition_list'] = transition_options

        return {
            'ranking_options': transition_options  # Pass to the template
        }
    
    def before_next_page(player, timeout_happened):
        # Store the ranking in participant vars so it's accessible in other apps
        player.participant.vars['transition_order'] = player.transition_order


page_sequence = [
    RankingPageA,
    RankingPageB
]