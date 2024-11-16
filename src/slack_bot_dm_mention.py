# This is a scafold for a simply slack bot that will respond to
# - direct messages
# - mentions in channels (or messages on threads where the bot was previously mentioned)

import os
import array
from dotenv import load_dotenv
load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])
memory = {}

def generate_response(user_input: str, context_id: str) -> str | None:
    if context_id not in memory:
        memory[context_id] = []
    # Store the user input in the context
    memory[context_id].append(user_input)

    # Here is where you can implement your business logic
    response = "Your response after running a business logic"

    # Store our response in the context
    memory[context_id].append(response)
    return response

@app.event("message")
def handle_message_events(event, say):
    print(f"Received Slack event: {event}")
    if event['channel_type'] == 'im':
        handle_direct_message_event(event, say)
    if event['channel_type'] == 'group':
        handle_channel_message_event(event, say)

@app.event("app_mention")
def handle_mention_events(event, say):
    if event.get('thread_ts') is None:
        # This is a mention at the top level, we should respond using this top level message id as context
        response = generate_response(event['text'], f"mention-{event['ts']}")
        say(text = response, thread_ts = event['ts'])
    else:
        # This is a mention within a thread, we should respond with the thread id as context
        response = generate_response(event['text'], f"mention-{event['thread_ts']}")
        say(text = response, thread_ts = event['thread_ts'])
    

def handle_direct_message_event(event, say):
    # This is a direct message, we should respond with the user id as context
    response = generate_response(event['text'], f"dm-{event['user']}")
    say(response)

def handle_channel_message_event(event, say):
    if event.get('thread_ts') is None:
        # This is a top-level channel message. We should do nothing since we only respond to direct mentions
        return
    else:
        # This is a thread message where we are not mentioned. Check if we were mentioned before; if yes, respond
        context = get_context(f"mention-{event['thread_ts']}")
        if context is not None:
            response = generate_response(event['text'], f"mention-{event['thread_ts']}")
            say(text = response, thread_ts = event['thread_ts'])

def get_context(context_id: str) -> array[str] | None:
    return memory[context_id]

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
