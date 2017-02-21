import ConfigParser
import json
import twitter
import re
import time
import argparse


def setupTwitter():
    config = ConfigParser.RawConfigParser()
    config.read('twitter.cfg')

    token = config.get('Twitter API', 'token')
    token_key = config.get('Twitter API', 'token_key')
    consumer_key = config.get('Twitter API', 'consumer_key')
    consumer_secret = config.get('Twitter API', 'consumer_secret')

    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=token,
                      access_token_secret=token_key)
    return api


def getTeamAccounts():
    with open('team_accounts.json', 'rb') as jsonfile:
        team_accounts = json.loads(jsonfile.read())
    return team_accounts


def addTeamAccount(team_name, team_account):
    if team_account[0] == '@':
        team_account = team_account[1:]
    team_accounts[team_name] = team_account
    with open('team_accounts.json', 'wb') as jsonfile:
        jsonfile.write(json.dumps(team_accounts, sort_keys=True, indent=4, separators=(',', ': ')))


def getScore(team_a, team_b):
    team_a_account = team_accounts[team_a]
    team_b_account = team_accounts[team_b]
    team_a_tweets = getTeamTweets(team_a_account)
    team_b_tweets = getTeamTweets(team_b_account)
    team_a_scores = extractTeamScores(team_a_tweets)
    team_b_scores = extractTeamScores(team_b_tweets)
    score = reconcileScores(team_a_scores, team_b_scores)
    team_a_score = score[0]
    team_b_score = score[1]
    print '%s %s - %s %s' % (team_a, str(team_a_score), str(team_b_score), team_b)


def getSingleScore(team):
    team_account = team_accounts[team]
    team_tweets = getTeamTweets(team_account)
    team_scores = extractTeamScores(team_tweets)
    score = team_scores[0][0]
    print '%s %s - %s Faceless Opponent' % (team, str(score[0]), str(score[1]))


def getTeamTweets(team_account):
    query = 'q=from%3A' + team_account + '%20-filter%3Aretweets%20-filter%3Areplies'
    results = api.GetSearch(raw_query=query)
    tweets = []
    for i in range(5):
        tweets.append([results[i].text, results[i].created_at_in_seconds])
    return tweets


def extractTeamScores(team_tweets):
    team_scores = []
    for tweet_obj in team_tweets:
        tweet = tweet_obj[0]
        date = tweet_obj[1]
        score = parseTweet(tweet)
        if score:
            team_scores.append([score, date])
    return team_scores


def parseTweet(tweet):
    score_string = re.findall(r'\d+-\d+', tweet)
    if len(score_string) == 1:
        numbers = score_string[0].split('-')
        scores = []
        for i in numbers:
            scores.append(int(i))
        return scores
    numbers = re.findall(r'\d+', tweet)
    if len(numbers) == 1:
        tied_at = int(numbers[0])
        if tied_at < 18:
            scores = [tied_at, tied_at]
            return scores


def reconcileScores(team_a_scores, team_b_scores):
    now = int(time.time())
    team_a_date = 0
    team_b_date = 0
    if len(team_a_scores) == 0 & len(team_b_scores) == 0:
        score = [0, 0]
        return score
    elif len(team_a_scores) > 0:
        team_a_latest_score = team_a_scores[0][0]
        team_a_date = team_a_scores[0][1]
        team_a_score_total = team_a_latest_score[0] + team_a_latest_score[1]
    elif len(team_b_scores) > 0:
        team_b_latest_score = team_b_scores[0][0]
        team_b_date = team_b_scores[0][1]
        team_b_score_total = team_b_latest_score[0] + team_b_latest_score[1]
    if ((now - team_a_date) > 720) & ((now - team_b_date) > 720):
        score = [0, 0]
    elif len(team_a_scores) == 0:
        score = [team_b_latest_score[1], team_b_latest_score[0]]
    elif len(team_b_scores) == 0:
        score = team_a_latest_score
    elif team_a_date - team_b_date >= 360:
        score = team_a_latest_score
    elif team_b_date - team_a_date >= 360:
        score = [team_b_latest_score[1], team_b_latest_score[0]]
    elif team_a_score_total >= team_b_score_total:
        score = team_a_latest_score
    else:
        score = [team_b_latest_score[1], team_b_latest_score[0]]
    return score


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get the score of a college ultimate game directly from teams\' Twitter feeds')
    subparsers = parser.add_subparsers(dest='command', help='Choose whether you want to check a score or add a team')
    score_parser = subparsers.add_parser('score', help='Check the score of a game')
    score_parser.add_argument('team_a', metavar='TEAM1', type=str, help='The first team')
    score_parser.add_argument('team_b', metavar='TEAM2', type=str, nargs='?', help='The second team')
    new_parser = subparsers.add_parser('add-team', help='Add a new team Twitter account to the database')
    new_parser.add_argument('team_name', metavar='TEAM', type=str)
    new_parser.add_argument('team_account', metavar='@HANDLE', type=str)
    args = parser.parse_args()
    print args

    api = setupTwitter()
    team_accounts = getTeamAccounts()

    if args.command == 'score':
        if args.team_b:
            team_a = args.team_a
            team_b = args.team_b
            getScore(team_a, team_b)
        elif args.team_a:
            team_a = args.team_a
            getSingleScore(team_a)
    elif args.command == 'add-team':
        team_name = args.team_name
        team_account = args.team_account
        addTeamAccount(team_name, team_account)
        print 'Added %s to database' % team_name
