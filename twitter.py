import snscrape.modules.twitter as sntwitter
import pandas as pd
import argparse
import os

from tqdm import tqdm


query = "Bitcoin lang:en until:2022-12-01 since:2022-01-01"

default_limit = 10000

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--word", required=False, type=str, default='Bitcoin')
    parser.add_argument("-f", "--since", required=False, type=str, default='2022-07-07')
    parser.add_argument("-t", "--to", required=False, type=str, default='2022-07-08')
    parser.add_argument("-l", "--limit", required=False, type=int, default=default_limit)

    args = parser.parse_args()

    date_list = pd.date_range(start=args.since, end=args.to)
    for idx, date in tqdm(enumerate(date_list[:-1])):

        tweets = []
        _since, _to = str(date)[:10], str(date_list[idx+1])[:10]
        # update query
        query = args.word + " lang:en until:" + _to + " since:" + _since
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            if(len(tweets) % 500 == 0):
                print(f'\nepoch #{len(tweets)}')

            # break
            if len(tweets) == args.limit:
                break
            else:
                tweets.append([tweet.date, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount])
                
        df = pd.DataFrame(tweets, columns=['Date', 'Tweet', 'like', 'retweet', 'reply'])
        
        limit_str = '' if args.limit == default_limit else '_' + str(args.limit)
        file_name = 'tweets_' + args.word + '_' + _since + '_' + _to + limit_str + '.csv'
        folder_path = './tweet_data/'

        # to save to csv
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        df.to_csv(folder_path + file_name)