
import os
import logging

# For local testing
from pathlib import Path
from dotenv import load_dotenv

from slack_bolt import App

from pprint import pprint

# For local testing
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.DEBUG) 

# Initializes your app with your bot token and signing secret
app = App(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
        )


@app.message(":wave:")
def say_hello(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")


# Add a new suggestion
def add_suggestion(new_suggestion,block):
    position_new_suggestion = 4 # from the back
    size_wo_suggestion = 5
    options = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]

    new_suggestion_dict = {
            "type": "section",
            "block_id": f"{options[len(block) - size_wo_suggestion]}",
            "text": {
                "type": "mrkdwn",
                "text": f":{options[len(block) - size_wo_suggestion]}: {new_suggestion} \n"
                },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "vote count: 0"
                    },
                "action_id": "voted"
                }
            }

    block.insert(len(block) - position_new_suggestion, new_suggestion_dict)
    return block


def remove_suggestion(new_suggestion,block):
    options = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    counter = 0

    for section in block:

        if section['block_id'] in options:
            print("WTF")
            print(new_suggestion)
            print(section['text']['text'][6:-2])
            if new_suggestion == section['text']['text'][len(section['block_id']) + 3:-2]:
                block.pop(counter)

        counter += 1

    return block


# Add a new vote
def change_vote(ID,blocks,user,user_id):
    for block in blocks:
        if block['block_id'] == ID:
            pprint(block['text']['text'])
            if f"<@{user_id}>" not in block['text']['text'].split(" "):
                block['text']['text'] = block['text']['text'] + f" <@{user}>"
                block['accessory']['text']['text'] = "vote count: " + str( int(block['accessory']['text']['text'].split(" ")[2]) + 1)
            else:
                block['text']['text'] = block['text']['text'].replace(f" <@{user_id}>", "")
                pprint(block['text']['text'])
                block['accessory']['text']['text'] = "vote count: " + str( int(block['accessory']['text']['text'].split(" ")[2]) - 1)

    return blocks


def add_question(question,block):
    new_question_dict = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{question}* \n"
                }
            }
    block.pop(0)
    block.insert(0,new_question_dict)
    return block


# Command to activate poll
@app.command("/poll")
def message_hello(command, say, ack, logger, body):
    user = command['user_name']

    ack()
    logger.info(body)
    say(
        blocks=[
            {
                "dispatch_action": True,
                "type": "input",
                "block_id": "question",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "question_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Type your question here"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Question",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "block_id":"suggested_v",
                "element": {
                    "type": "plain_text_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Add Suggestion",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Add Suggestion"
                        },
                        "style": "primary",
                        "action_id": "add_suggested"
                    },
                    # {
                    #     "type": "button",
                    #     "text": {
                    #         "type": "plain_text",
                    #         "emoji": True,
                    #         "text": "Remove Suggestion"
                    #     },
                    #     "style": "danger",
                    #     "action_id": "remove_suggested"
                    # }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"Poll created by <@{user}>",
                        "emoji": True
                    }
                ]
            }
        ],
        text="Somebody started a new poll!"	
    )

@app.action("add_suggested")
def getting_suggestion(body, ack, respond, say):
    ack()

    new_suggestion = body['state']['values']['suggested_v']['input']['value']
    old_block = body['message']['blocks']

    respond(replace_original=True,blocks=add_suggestion(new_suggestion,old_block))


@app.action("remove_suggested")
def removing_suggestion(body, ack, respond, say):
    ack()

    new_suggestion = body['state']['values']['suggested_v']['input']['value']
    old_block = body['message']['blocks']

    respond(replace_original=True,blocks=remove_suggestion(new_suggestion,old_block))


@app.action("voted")
def handle_vote(ack, body, respond):
    ack()

    vote_ID = body['actions'][0]['block_id']
    old_block = body['message']['blocks']
    user = body['user']['username']
    user_id = body['user']['id']
    respond(replace_original=True, blocks=change_vote(vote_ID,old_block,user,user_id))


@app.action("question_input")
def getting_question(body, ack, respond, say):
    ack()
    pprint(body['state']['values'])
    question = body['state']['values']['question']['question_input']['value']
    old_block = body['message']['blocks']

    respond(replace_original=True,blocks=add_question(question,old_block))


# handling "message" event which is triggered on every action
# @app.event("message")
# def handle_message_events(body, logger):
#     logger.info(body)



# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 5002)))


# from flask import Flask, request
# from slack_bolt.adapter.flask import SlackRequestHandler

# flask_app = Flask(__name__)
# handler = SlackRequestHandler(app)


# @flask_app.route("/slack/events", methods=["POST"])
# def slack_events():
#     return handler.handle(request)
