# -*- coding: utf-8 -*-
from django.shortcuts import render
import json, requests, random, re
from pprint import pprint
from string import punctuation
from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
PAGE_ACCESS_TOKEN = "EAAXJ8gI90ZBMBAE3TYgXaIRpEYyHZCLp0yWRbkbE0RJ6C2DTuVTxvSaSueHq0x6IMHmCcMMOzZCv7wYR3kGWUmIAM1JyInZBH1vR4ndJbUrbi4O0ZBOf8hZB1ePdHjZCRTS5j5pELuQLp9X4ehQv2JHMMFJdZCXagepuZBkd37IBN1wZDZD"
VERIFY_TOKEN = "0123456789"

responses_to_payload= {'cost':{'':json.dumps({"text":"A or B","quick_replies":[{"content_type":"text","title":"A", "payload":"cost a"},{"content_type":"text","title":"B", "payload":"cost b"}]})
,'a':json.dumps({"text":"""Σαν διαδικασια κοστιζει 430 ευρω με ολα τα μαθηματα θεωρητικα πρακτικα κ παρασταση. Τα παραβολα και οι γιατροι ειναι +150 ευρω (χωρις προμηθεια τραπεζας +10ευρω)"""})
,'b':json.dumps({"text":"""Σαν διαδικασια κοστιζει 500 ευρω με ολα τα μαθηματα θεωρητικα πρακτικα κ παρασταση. Τα παραβολα και οι γιατροι ειναι +200 ευρω (χωρις προμηθεια τραπεζας +10ευρω)"""})
},
'help':json.dumps({"text":"'βοήθια','κόστος'","quick_replies":[{"content_type":"text","title":"help", "payload":"help"},{"content_type":"text","title":"cost", "payload":"cost"}]})
}
responses={'bot':json.dumps({"text":"how can i help?","quick_replies":[{"content_type":"text","title":"tell me the cost", "payload":"cost"},{"content_type":"text","title":"tell me the commands commands","payload":"help"}]})}
#responses.update('':json.dumps({"text":"how can i help"}))

# Create your views here.
def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)
def post_facebook_message(message_to_send,fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":json.loads(message_to_send)})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())
def get_deepest_value_in_dict(tokens,dic):
    length = len(tokens)
    value=''
    if (length == 0)&( '' in dic):
        temp_value = dic['']
    elif length == 0:
         temp_value = dic
    elif (length>0 )&( tokens[0] in dic):
        temp_value = dic[tokens[0]]
    elif '' in dic:
        temp_value = dic['']
    else:
        temp_value = dic


    if (type(temp_value)==type(dict()))&(length>0):
        value = get_deepest_value_in_dict(tokens[1:],temp_value)
    else:
        value=temp_value
    return value
def find_responces_and_send_them(fbid,text,responses):
    tokens = strip_punctuation(text).lower().split()
    text=''
    for i in range(0,len(tokens)):
        token = tokens[i]
        if token in responses:
            temp_text=get_deepest_value_in_dict(tokens[i:],responses)
            print(temp_text)
            post_facebook_message(temp_text,fbid)
    if not text:
            text="επιλογες:'κόστος'"

def handle_payload(fbid,payload):
    find_responces_and_send_them(fbid,payload,responses_to_payload)

def handle_facebook_message(fbid, recevied_message):
    find_responces_and_send_them(fbid,recevied_message,responses)

    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
def handle_message(message):
    if ('quick_reply' in message['message']):
         if('payload' in message['message']['quick_reply']):
             handle_payload(message['sender']['id'], message['message']['quick_reply']['payload'])
             return
    handle_facebook_message(message['sender']['id'], message['message']['text'])

class MessengerBot(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '0123456789':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        pprint(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    #pprint(message)
                    handle_message(message)
        return HttpResponse()
