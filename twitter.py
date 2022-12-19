import snscrape.modules.twitter as sntwitter
import pandas as pd
import argparse
import os
import multiprocessing
import datetime
from functools import partial

from tqdm import tqdm


def scrape_one_day(since_to, limit, word):
        _since, _to = since_to[0], since_to[1]  
        tweets = []
        # update query
        query = word + " lang:en until:" + _to + " since:" + _since
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            # break
            if len(tweets) == limit:
                break
            else:
                tweets.append([tweet.date, tweet.content, tweet.likeCount, tweet.retweetCount, tweet.replyCount])
            # if(len(tweets) % 500 == 0):
            #     print(len(tweets))
                
        df = pd.DataFrame(tweets, columns=['Date', 'Tweet', 'like', 'retweet', 'reply'])
        
        # limit_str = '' if args.limit == default_limit else '_' + str(args.limit)
        limit_str = ''
        file_name = 'tweets_' + word + '_' + _since + '_' + _to + limit_str + '.csv'
        folder_path = './tweet_data/'

        # to save to csv
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        df.to_csv(folder_path + file_name)

        # with lock:
        #     finished_process += 1
        #     print(finished_process / len(query_list) *100, '%', flush=True)

if __name__ == '__main__':
    PROCESSES_NUM = 4
    query = "Bitcoin lang:en until:2022-12-01 since:2022-01-01"
    default_limit = 10000
    
    # manager = multiprocessing.Manager()
    # finished_process = manager.Value('i', 0)
    # lock = manager.Lock()


    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--word", required=False, type=str, default='Bitcoin')
    parser.add_argument("-f", "--since", required=False, type=str, default='2022-07-07')
    parser.add_argument("-t", "--to", required=False, type=str, default='2022-07-08')
    parser.add_argument("-l", "--limit", required=False, type=int, default=default_limit)
    parser.add_argument("-p", "--process", required=False, type=int, default=PROCESSES_NUM)

    args = parser.parse_args()

    date_list = pd.date_range(start=args.since, end=args.to)
    query_list = []
    for date in (date_list[:-1]):

        _since, _to = str(date)[:10], str(date+datetime.timedelta(days=1))[:10]
        query_list.append([_since, _to])



    # multiprocessing pool object
    pool = multiprocessing.Pool()
    print(args.process)
    # pool object with number of element
    pool = multiprocessing.Pool(processes=args.process)

    # map the function to the list and pass
    # function and input list as arguments
    r = list(tqdm(pool.imap(partial(scrape_one_day, limit=args.limit, word=args.word), query_list), total=len(query_list)))

    pool.close()