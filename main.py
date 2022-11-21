import argparse
import csv
import os
import hashlib
from datetime import datetime, timedelta
from pytz import timezone
from slack_sdk import WebClient


SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
TIMEZONE = os.environ.get("TIMEZONE")


def parse_data():
    with open("data.csv", newline="") as csvfile:
        data = [x for x in csv.reader(csvfile)]
    holidays = {}
    for h in data[2:]:
        start = datetime.strptime(h[1], "%Y-%m-%d")
        end = datetime.strptime(h[2], "%Y-%m-%d")
        while start <= end:
            iterstr = start.strftime("%Y-%m-%d")
            holidays[iterstr] = holidays.get(iterstr, [])
            holidays[iterstr].append(h[0])
            start += timedelta(days=1)
    return data[0], data[1], holidays


def pick_people(peeps_set, holidays, when=None):
    if not when:
        when = datetime.now()
    a = hashlib.sha256(bytes(when.strftime("%Y-%m-%d"), "utf-8")).hexdigest()
    res = []
    for b in a:
        intval = int(b, 16)
        if intval not in res and intval < len(peeps_set):
            res.append(intval)

    for x in range(len(peeps_set)):
        if x not in res:
            res.append(x)

    return [peeps_set[a] for a in res if peeps_set[a] not in holidays]


def insert_to_slack(names, when, slack_client):
    msg = "Standup roulette results: " + ", ".join(names)
    result = slack_client.chat_scheduleMessage(
        channel=CHANNEL_ID, text=msg, post_at=when.strftime("%s")
    )
    print(result)


def run(cli, offset, days_ahead, dry_run=False):
    names, times, holidays = parse_data()
    start = datetime.now(timezone(TIMEZONE))

    for i in range(0 + offset, days_ahead + offset):
        when = start + timedelta(days=i)
        day_position = int(when.strftime("%w"))
        if day_position in [0, 6]:
            continue
        when = when.replace(
            hour=int(times[day_position - 1].split(":")[0]),
            minute=int(times[day_position - 1].split(":")[1]),
            second=0,
        )
        standup_names = pick_people(
            names, holidays.get(when.strftime("%Y-%m-%d"), []), when
        )
        if not dry_run:
            insert_to_slack(standup_names, when, cli)


def list_scheduled(client):
    start = datetime.now()
    result = client.chat_scheduledMessages_list(
        channel_id=CHANNEL_ID,
        latest=(start + timedelta(days=60)).strftime("%s"),
        oldest=start.strftime("%s"),
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true", help="Slack messages won't get created."
    )
    parser.add_argument(
        "-o", "--offset", default=0, type=int, help="Days ahead when to start"
    )
    parser.add_argument(
        "-a", "--days-ahead", default=30, type=int, help="How many days to schedule"
    )
    parser.add_argument(
        "--show-scheduled",
        action="store_true",
        help="Show all scheduled messages and exit.",
    )

    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Remove all scheduled messages and schedule again.",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Remove all scheduled messages.",
    )

    args = parser.parse_args()
    slack_cli = WebClient(token=SLACK_TOKEN)
    if args.show_scheduled:
        print(list_scheduled(slack_cli))
        exit()
    if args.clear:
        clear_schedule(slack_cli)
        exit()
    if args.refresh:
        clear_schedule(slack_cli)
    run(slack_cli, args.offset, args.days_ahead, dry_run=args.dry_run)
