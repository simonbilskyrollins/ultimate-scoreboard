import ConfigParser
import twitter
import re
import time
import sys

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

team_accounts = {'Carleton': 'cutrules',
                 'Wisconsin': 'hodaglove',
                 'UNC-Wilmington': 'seamenultimate',
                 'Auburn': 'AuburnUltimate',
                 'Cal Poly-SLO': 'CORE_ultimate',
                 'Connecticut': 'UConnGrind',
                 'Case Western Reserve': 'FightingGobies',
                 'Massachusetts': 'UMassUltimate',
                 'Utah': 'ZCU_Ultimate',
                 'North Carolina': 'UNC_Darkside',
                 'Florida State': 'DUFtrainroll',
                 'Texas A&M': 'DozenUltimate',
                 'Michigan': 'magnUMultimate',
                 'Minnesota': '1Duck1Love',
                 'Oregon': 'egotime',
                 'Colorado': 'CUMamabird',
                 'Harvard': 'HarvardRedLine',
                 'Washington': 'sundodgers',
                 'Pittsburgh': 'Pittultimate',
                 'Georgia': 'jojahultimate',
                 'Florida': 'FloridaUltimate'}


def getTeamTweets(team_account):
    query = 'q=from%3A' + team_account + '%20-filter%3Aretweets%20-filter%3Areplies'
    results = api.GetSearch(raw_query=query)
    tweets = []
    for i in range(5):
        tweets.append([results[i].text, results[i].created_at_in_seconds])
    return tweets


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


def extractTeamScores(team_tweets):
    team_scores = []
    for tweet_obj in team_tweets:
        tweet = tweet_obj[0]
        date = tweet_obj[1]
        score = parseTweet(tweet)
        if score:
            team_scores.append([score, date])
    return team_scores


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        team_a = sys.argv[1]
        team_b = sys.argv[2]
        getScore(team_a, team_b)
    elif len(sys.argv) == 2:
        team_a = sys.argv[1]
        getSingleScore(team_a)
