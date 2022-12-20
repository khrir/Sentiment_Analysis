import tweepy, datetime, re
import pandas as pd
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from dotenv import dotenv_values

config = dotenv_values('.env')

CONSUMER_KEY = config['CONSUMER_KEY']
CONSUMER_SECRET = config['CONSUMER_SECRET']
ACCESS_TOKEN = config['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = config['ACCESS_TOKEN_SECRET']

count = 1000
keyword = 'Qatar'

class TweetAnalyzer():

  def __init__(self, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    '''
      Conectar com o tweepy
    '''
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    self.conToken = tweepy.API(auth, wait_on_rate_limit=True, retry_count=5, retry_delay=10)

  def __clean_tweet(self, tweets_text):
    '''
    Tweet cleansing.
    '''
    clean_text = re.sub(r'RT+', '', tweets_text) 
    clean_text = re.sub(r'@\S+', '', clean_text)  
    clean_text = re.sub(r'https?\S+', '', clean_text) 
    clean_text = clean_text.replace("\n", " ")

    return clean_text

  def search_by_keyword(self, keyword, count):
    '''
      Search for the twitters thar has commented the keyword subject.
    '''
    tweets_iter = tweepy.Cursor(self.conToken.search_tweets,
                          q=keyword, tweet_mode='extended',
                          result_type='mixed',
                          lang='en', include_entities=True).items(count)

    return tweets_iter

  def prepare_tweets_list(self, tweets_iter):
    '''
      Transforming the data to DataFrame.
    '''

    tweets_data_list = []
    for tweet in tweets_iter:
      if not 'retweeted_status' in dir(tweet):
        tweet_text = self.__clean_tweet(tweet.full_text)
        tweets_data = {
            'len' : len(tweet_text),
            'ID' : tweet.id,
            'User' : tweet.user.screen_name,
            'UserName' : tweet.user.name,
            'UserLocation' : tweet.user.location,
            'TweetText' : tweet_text,
            'Language' : tweet.user.lang,
            'Date' : tweet.created_at,
            'Source': tweet.source,
            'Likes' : tweet.favorite_count,
            'Retweets' : tweet.retweet_count,
            'Coordinates' : tweet.coordinates,
            'Place' : tweet.place 
        }

        tweets_data_list.append(tweets_data)

    return tweets_data_list

  def sentiment_polarity(self, tweets_text_list):
      tweets_sentiments_list = []

      for tweet in tweets_text_list:
        polarity = TextBlob(tweet)

        if polarity.polarity > 0:  # type: ignore
          tweets_sentiments_list.append('Positive')
        elif polarity.polarity < 0:  # type: ignore
          tweets_sentiments_list.append('Negative')
        else:
          tweets_sentiments_list.append('Neutral')

      return tweets_sentiments_list

analyzer = TweetAnalyzer(CONSUMER_KEY = CONSUMER_KEY, CONSUMER_SECRET = CONSUMER_SECRET, ACCESS_TOKEN = ACCESS_TOKEN, ACCESS_TOKEN_SECRET = ACCESS_TOKEN_SECRET)

# Para realizar as buscas usando a keyword e quantidade predefinida e converter em uma lista.
tweets_iter = analyzer.search_by_keyword(keyword, count)
tweets_list = analyzer.prepare_tweets_list(tweets_iter)

# Uso de um Dataframe para melhor manipulação
tweets_df = pd.DataFrame(tweets_list)

# Chamar a função para análise de sentimentos
tweets_df['Sentiment'] = analyzer.sentiment_polarity(tweets_df['TweetText'])

tweets_df.to_csv('pesquisa1.csv')

print(tweets_df.head())