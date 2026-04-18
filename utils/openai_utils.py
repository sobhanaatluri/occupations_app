import openai
import os

def set_openai_key():
    """ Ensures OpenAI API key is set only once per session. """
    #print("OpenAI key setting")
    if openai.api_key != os.environ['OPEN_AI_KEY']:
        #print("Setting First time")
        openai.api_key = os.environ['OPEN_AI_KEY']
    #else:
        #Sprint("Already Set")
        