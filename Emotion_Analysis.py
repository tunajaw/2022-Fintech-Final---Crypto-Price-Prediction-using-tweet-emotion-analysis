import glob
import pandas as pd
import preprocessor as p
import nltk
import re
import emojis
import csv
import collections
import json
import argparse
import os
from ekphrasis.classes.segmenter import Segmenter
from textblob import TextBlob, Word
from nltk import word_tokenize
from nltk.corpus import stopwords
from tqdm import tqdm


#Extract the text in the hashtag
def extract_hashtag_text(tweet):
    tag_text = ""
    tweet= re.findall(r'#(\w+)', tweet)
    for tag in tweet:
        clean_tag=seg.segment(tag)
        tag_text += (clean_tag + " ")
    return tag_text

#Extract text information in emoji
def extract_emoji_text(tweet):
    emoji_text = ""
    emoji_list = emojis.get(tweet)
    for emoji in emoji_list:
        emoji = emojis.decode(emoji)
        emoji = re.sub(r':', '', emoji) 
        emoji = re.sub(r'_', ' ', emoji) 
        emoji_text += (emoji + " ")
    return emoji_text

#Clean up irrelevant symbols in tweets
def tweets_cleaner(tweet):
    #Use preprocessor to clean up URLs, Hashtags and user mentions
    tweet = p.clean(tweet)
    #Clean up all numbers
    tweet = re.sub(r'[0-9]*', '', tweet) 
    #Clean up all punctuation
    tweet = re.sub(r'[^\w\s]', '', tweet) 
    #Lowercase letters
    semiclean_tweet = tweet.lower()
    return semiclean_tweet

#Lemmatization
def lemmatization_without_stopwords(semiclean_tweet):
    lemmatized_list=[]
    #Use TextBlob to tokenize tweets
    sent = TextBlob(semiclean_tweet)
    tag_dict = {"J": 'a', 
                "N": 'n', 
                "V": 'v', 
                "R": 'r'}
    #Realize lemmatization according to the corresponding POS
    words_and_tags = [(w, tag_dict.get(pos[0], 'n')) for w, pos in sent.tags]
    #Remove stopwords
    for wd, tag in words_and_tags:
        if wd  not in stopwords:
            lemmatized_list.append(wd.lemmatize(tag))
    return lemmatized_list

#Get clean tweet word lists
def get_clean_text(raw_daily_data):
    
    clean_text=[0]*len(raw_daily_data["Tweet"])
    
    for num, tweet in enumerate(raw_daily_data["Tweet"]):
        t_ls = lemmatization_without_stopwords(tweets_cleaner(tweet))
        e_ls = lemmatization_without_stopwords(extract_emoji_text(tweet))
        h_ls = lemmatization_without_stopwords(extract_hashtag_text(tweet))
        clean_text[num] = t_ls + e_ls + h_ls
    
    return clean_text

#Get the emotion score of each tweet
def get_emotion_score(dataframe,clean_text):
    
    anger_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            anger_score[i] += anger_dict.get(word, 0) * freq

    anticipation_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            anticipation_score[i] += anticipation_dict.get(word, 0) * freq
            
    disgust_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            disgust_score[i] += disgust_dict.get(word, 0) * freq
    
    fear_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            fear_score[i] += fear_dict.get(word, 0) * freq
    
    joy_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            joy_score[i] += joy_dict.get(word, 0) * freq
    
    sadness_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            sadness_score[i] += sadness_dict.get(word, 0) * freq
            
    surprise_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            surprise_score[i] += surprise_dict.get(word, 0) * freq
    
    trust_score = [0]*len(clean_text)
    for i, clean in enumerate(clean_text):
        counts = collections.Counter(clean)
        for word, freq in counts.items():
            trust_score[i] += trust_dict.get(word, 0) * freq
            
    dataframe['anger_score']=anger_score  
    dataframe['anticipation_score']=anticipation_score
    dataframe['disgust_score']=disgust_score
    dataframe['fear_score']=fear_score
    dataframe['joy_score']=joy_score
    dataframe['sadness_score']=sadness_score
    dataframe['surprise_score']=surprise_score
    dataframe['trust_score']=trust_score 

#Get the emotion score of the day
def get_daily_emotion(emotion_df):
    d_anger_score=0
    d_anticipation_score=0
    d_disgust_score=0
    d_fear_score=0
    d_joy_score=0
    d_sadness_score=0
    d_surprise_score=0
    d_trust_score=0
    
    for i in range(0,len(emotion_df)):
        d_anger_score += (1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['anger_score']
        #Use like as an additional weight for tweets, and each like represents 1% of the sentiment score
        d_anticipation_score += (1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['anticipation_score']
        d_disgust_score +=(1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['disgust_score']
        d_fear_score +=(1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['fear_score']
        d_joy_score +=(1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['joy_score']
        d_sadness_score +=(1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['sadness_score']
        d_surprise_score +=(1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['surprise_score']
        d_trust_score +=(1+0.01*emotion_df.iloc[i]['like'])*emotion_df.iloc[i]['trust_score']
    
    return d_anger_score,d_anticipation_score,d_disgust_score,d_fear_score,d_joy_score,d_sadness_score,d_surprise_score,d_trust_score

#Get valid tweet data
def get_available_emotion(df):
    available_daily_data = df[ (df['anger_score'] != 0) | (df['anticipation_score']!=0) | (df['disgust_score']!=0) | (df['fear_score']!=0)| (df['joy_score']!=0) | (df['sadness_score']!=0) | (df['surprise_score']!=0) | (df['trust_score'] != 0)]
    return available_daily_data



if __name__ == "__main__":

    # defince arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=False, type=str, default='./tweet_data/')
    parser.add_argument("-m", "--month", required=True, type=int)
    args = parser.parse_args()

    # Preloading packages
    stopwords = stopwords.words('english')
    seg = Segmenter(corpus='twitter')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

    #Read the emotion corpus
    with open('emotion_dicts.txt', 'r') as f:
        emotion_dict = json.loads(f.read())

    anger_dict = emotion_dict['anger']
    anticipation_dict = emotion_dict['anticipation']
    disgust_dict = emotion_dict['disgust']
    fear_dict = emotion_dict['fear']
    joy_dict = emotion_dict['joy']
    sadness_dict = emotion_dict['sadness']
    surprise_dict = emotion_dict['surprise']
    trust_dict = emotion_dict['trust']

    daily_emotion=pd.DataFrame(
        columns=(
            'date','volume','available_volume','anger_score','anticipation_score',
            'disgust_score','fear_score','joy_score','sadness_score','surprise_score','trust_score'
        )
    )
    
    filenames = glob.glob(args.path + '*.csv') 
    for filename in tqdm(filenames):
        
        # Get daily clean tweet
        daily_data = pd.read_csv(filename, index_col=0)
        # Get date
        date = daily_data['Date'][0][:10]
        # Emotion score
        clean_text = get_clean_text(daily_data)
        get_emotion_score(daily_data, clean_text)
        anger_score,anticipation_score,disgust_score,fear_score,joy_score,sadness_score,surprise_score,trust_score = get_daily_emotion(daily_data)
        # Tweets volume
        volume=len(daily_data)
        # Available tweets volume (including specific emotions)
        available_volume=len(get_available_emotion(daily_data))
        # put result in dataframe
        daily_emotion= daily_emotion.append({'date' : date , 'volume' :volume , 'available_volume': available_volume,
                                         'anger_score' : anger_score , 'anticipation_score' : anticipation_score ,
                                         'disgust_score': disgust_score , 'fear_score' : fear_score ,
                                         'joy_score' : joy_score , 'sadness_score': sadness_score,
                                         'surprise_score' : surprise_score , 'trust_score': trust_score}, 
                                         ignore_index = True)

    folder_path = './emotion_data/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # output file
    daily_emotion.to_csv(folder_path + str(args.month) + '.csv')
