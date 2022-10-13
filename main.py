
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