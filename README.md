# Simple Slack standup roulette

Randomiser of names for standup to remove bias in ordering in an attempt to make standups smoother.

## Prerequisites
**Python 3.11** - should work fine on earliers versions but I tested it only on 3.11 and 3.10  
**Slack App** - Go to https://api.slack.com/apps, create new app, grab tokens. Then I had to add it to my slack space and for private channel to manually add slack app user to the channel so it can see it. Otherwise it claimed that the channel didn't exist.



## Setup
First install all dependencies, ideally in some virtualenv.

### Create .env file
Copy .env.example and fill in the data, mainly from slack


### Create data.csv
Copy sample-data.csv to data.csv and modify to your needs.

sample-data.csv format explanation:
Row 1: list of all names in the team that take turn during the standup.
Row 2: list of all times when the standup message should be scheduled to Mon - Fri.
Row 3 - N: Name and holidays period when somebody is on holidays so it can be removed from the standup roulette. Name should be the same as in Row 1


## How to run:
1) make sure .env is loaded, maybe even through `direnv`.
2) `python main.py` by default it covers 30 days from today. Check with `--help` for more options


## Examples
### Running from today for 14 days
`python main.py -o 0 -a 14`

### Server says time is in the past
If you are running option `-o 0` and it is currently after the time specified in data.csv, please use `-o 1` like `python main.py -o 1`

### I made a change to the data.csv and messages can be affected
`python main.py --refresh` will first remove all channel messages and then scheudle new one.

### I'm just curious what's scheduled
`python main.py --show-schedule` . Script exits right after, nothing is changed.