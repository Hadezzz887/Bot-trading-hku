import snscrape.modules.twitter as sntwitter
from config import VIRAL_KEYWORDS

async def get_x_score(token_name):

    score = 0

    lower = token_name.lower()

    for word in VIRAL_KEYWORDS:
        if word in lower:
            score += 20

    try:

        query = token_name

        tweets = []

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):

            if i > 30:
                break

            tweets.append(tweet.content)

        engagement = len(tweets)

        score += min(engagement, 50)

    except:
        pass

    return min(score, 100)
