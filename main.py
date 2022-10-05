import csv
import clipboard
import hashlib
import time
from pynput import keyboard, mouse
from datetime import datetime, timedelta

DAYS_AHEAD = 5
DAYS_OFFSET = 17
SLEEP_SECONDS = 0.2
POSITIONS = {
    "slack_select": (134.65023803710938, 52.684173583984375),
    "slack_textbox": (416.0513916015625, 1037.39404296875),
    "schedule1": (1755.966796875, 1072.2340087890625),
    "schedule2": (1582.39404296875, 1040.10009765625),
    "date_select": (776.720947265625, 571.3927001953125),
    "time_select": (1012.1507568359375, 570.7311401367188),
    "schedule_button": (1049.039794921875, 638.9081420898438),
}


def parse_data():
    with open('data.csv', newline='') as csvfile:
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
    a = hashlib.sha256(bytes(when.strftime("%Y-%m-%d"), 'utf-8')).hexdigest()
    res = []
    for b in a:
        intval = int(b, 16)
        if intval not in res and intval < len(peeps_set):
            res.append(intval)

    for x in range(len(peeps_set)):
        if x not in res:
            res.append(x)

    return [peeps_set[a] for a in res if peeps_set[a] not in holidays]


def insert_to_slack(names, when):
    clipboard.copy(", ".join(names))
    mouse_ctrl = mouse.Controller()
    keyboard_ctrl = keyboard.Controller()
    mouse_ctrl.position = POSITIONS["slack_select"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.position = POSITIONS["slack_textbox"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(SLEEP_SECONDS)
    # TODO: Get this OS independent
    keyboard_ctrl.press(keyboard.Key.cmd.value)
    keyboard_ctrl.press("v")
    keyboard_ctrl.release("v")
    keyboard_ctrl.release(keyboard.Key.cmd.value)
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.position = POSITIONS["schedule1"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.position = POSITIONS["schedule2"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.position = POSITIONS["date_select"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    clipboard.copy(when.strftime("%Y-%m-%d"))
    keyboard_ctrl.press(keyboard.Key.cmd.value)
    keyboard_ctrl.press("v")
    keyboard_ctrl.release("v")
    keyboard_ctrl.release(keyboard.Key.cmd.value)
    time.sleep(SLEEP_SECONDS)
    clipboard.copy(when.strftime("%H:%M"))
    mouse_ctrl.position = POSITIONS["time_select"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(SLEEP_SECONDS)
    keyboard_ctrl.press(keyboard.Key.cmd.value)
    keyboard_ctrl.press("v")
    keyboard_ctrl.release("v")
    keyboard_ctrl.release(keyboard.Key.cmd.value)
    time.sleep(SLEEP_SECONDS)
    keyboard_ctrl.press(keyboard.Key.enter.value)
    keyboard_ctrl.release(keyboard.Key.enter.value)
    mouse_ctrl.position = POSITIONS["schedule_button"]
    time.sleep(SLEEP_SECONDS)
    mouse_ctrl.press(mouse.Button.left)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(SLEEP_SECONDS)


def run():
    names, times, holidays = parse_data()
    start = datetime.now()
    for i in range(0 + DAYS_OFFSET, DAYS_AHEAD + DAYS_OFFSET):
        when = start + timedelta(days=i)
        day_position = int(when.strftime("%w"))
        if day_position in [0, 6]:
            continue
        when = when.replace(
            hour=int(times[day_position - 1].split(":")[0]),
            minute=int(times[day_position - 1].split(":")[1])
        )
        standup_names = pick_people(names, holidays.get(when.strftime("%Y-%m-%d"), []), when)
        insert_to_slack(standup_names, when)


if __name__ == '__main__':
    run()
