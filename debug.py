import os
from slack_sdk import WebClient
from datetime import datetime, timedelta

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")


client = WebClient(token=SLACK_TOKEN)


def list_scheduled(client):
    start = datetime.now()
    result = client.chat_scheduledMessages_list(
        latest=(start + timedelta(days=60)).strftime("%s"), oldest=start.strftime("%s")
    )

    return result


def clear_schedule(client):
    """Handy if you messed up and need to reschedule messages again"""
    ids = [i["id"] for i in list_scheduled(client)["scheduled_messages"]]
    for i in ids:
        r = client.chat_deleteScheduledMessage(
            channel=CHANNEL_ID, scheduled_message_id=i
        )
        print(r)
