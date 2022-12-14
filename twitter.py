import snscrape.modules.twitter as sntwitter
import pandas as pd
import argparse


query = "Bitcoin lang:en until:2022-12-01 since:2022-01-01"
tweets = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--word", required=False, type=str, default='Bitcoin')
    parser.add_argument("-f", "--since", required=False, type=str, default='2022-07-07')
    parser.add_argument("-t", "--to", required=False, type=str, default='2022-07-08')
    parser.add_argument("-l", "--limit", required=False, type=int, default=100000)

    args = parser.parse_args()

    # update query
    query = args.word + " lang:en until:" + args.to + " since:" + args.since


    for tweet in sntwitter.TwitterSearchScraper(query).get_items():

        if(len(tweets) % 500 == 0):
            print(f'epoch #{len(tweets)}')
        
        # print(vars(tweet))

        # break
        if len(tweets) == args.limit:
            break
        else:
            tweets.append([tweet.date, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount])
            
    df = pd.DataFrame(tweets, columns=['Date', 'Tweet', 'like', 'retweet', 'reply'])
    
    limit_str = '' if args.limit == 100000 else '_' + str(args.limit)
    file_name = 'tweets_' + args.word + '_' + args.since + '_' + args.to + limit_str + '.csv'

    # to save to csv
    df.to_csv(file_name)