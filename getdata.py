import snscrape.modules.twitter as sntwitter
import pandas as pd
import sqlite3
import json

def search_on_twitter(what_do_you_search, limits = 100):
    
    tweets = []
    for tweet in sntwitter.TwitterSearchScraper(what_do_you_search).get_items():
        if len(tweets) == limits:
            break
        else:
            tweets.append([tweet.date, tweet.user.username, tweet.content])

    df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])
    
    df.to_json('data.json', orient = 'records')

    conn = sqlite3.connect('instance/twitter.db')
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    c = conn.cursor()
    print(data[0]['User'])
    for record in data:
        c.execute('INSERT INTO twitter (Date, User, Tweet) VALUES (?, ?, ?)',
                (record['Date'], record['User'], record['Tweet']))
    
    # Save the changes and close the connection
    conn.commit()
    conn.close()

    

def create_db():
    conn = sqlite3.connect('instance/twitter.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE twitter
             (Date DATE PRIMARY KEY,
              User TEXT,
              Tweet TEXT)''')
    conn.commit()
    conn.close()

#create_db()