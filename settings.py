from os import environ
import os
print(f"Initializing process: {os.getpid()}")

SESSION_CONFIGS = [
    
    dict(
        name= 'nova_version1',
        display_name= "Dimensions-Nova",
        num_demo_participants= 1,
        app_sequence= ['representations_v2', 'occupationinfo', 'representations_task_s_wa',
                       'go_no_go', 'representations_task_s_k', 'occupation_ranking', 'similarity_transition_ranking', 'values_ranking',
                       'attainable_occupation', 'dream_occupation', 'transition_q', 'representations_q_1'],
        completionlink = "https://app.prolific.com/submissions/complete?cc=CUMQ9XW6",
    ),
    
    dict(
        name= 'representations_v2',
        display_name= "representations_v2",
        num_demo_participants= 1,
        app_sequence= ['representations_v2'],
    ),
]


ROOMS = [
    dict(
        name='representations_nova_member',
        display_name='Occupational Similarity I',
    ),
    
    dict(
        name='representations_nova_staff',
        display_name='Occupational Similarity II',
    ),
]
'''
SESSION_CONFIGS = [
    dict(
        name= 'my_experiment',
        display_name= "My Experiment",
        num_demo_participants= 1,
        app_sequence= ['representations', 'representations_task'],
    ),
    
    dict(
        name= 'task',
        display_name= "task",
        num_demo_participants= 1,
        app_sequence= ['representations_task'],
    ),
    
    dict(
        name= 'questions',
        display_name= "questions",
        num_demo_participants= 1,
        app_sequence= ['representations_q'],
    ),
    
    dict(
        name= 'representations_survey',
        display_name= "Representations Survey",
        num_demo_participants= 1,
        app_sequence= ['representations', 'representations_task','representations_q'],
    ),
    
    dict(
        name= 'representations_v2',
        display_name= "representations_v2",
        num_demo_participants= 1,
        app_sequence= ['representations_v2'],
    ),
    
    dict(
        name= 'occupationinfo',
        display_name= "occupationinfo",
        num_demo_participants= 1,
        app_sequence= ['representations_v2','occupationinfo'],
    ),
    
    dict(
        name= 'representations_survey_v2',
        display_name= "Representations Survey Version 2",
        num_demo_participants= 1,
        app_sequence= ['representations_v2', 'occupationinfo', 'representations_task','representations_q'],
    ),
]
'''

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'nolab_sa'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
OTREE_PRODUCTION= 1
OTREE_AUTH_LEVEL= "STUDY"

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '9065579417948'

INSTALLED_APPS = ['otree']
