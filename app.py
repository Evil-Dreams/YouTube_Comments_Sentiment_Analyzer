from flask import Flask, render_template, request
from googleapiclient.discovery import build
from textblob import TextBlob
import pandas as pd
import re

app = Flask(__name__)

# Replace with your own YouTube Data API key
API_KEY = "AIzaSyDCDAIA_OZOwKW_Q_RgYWAxtWTH8QyrSEI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_comments(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    response = request.execute()

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

def analyze_sentiment(comments):
    data = []
    for text in comments:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0.2:
            sentiment = "Positive"
        elif polarity < -0.2:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        data.append({'text': text, 'sentiment': sentiment})
    return data

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['video_url']
    video_id = get_video_id(url)
    comments = get_comments(video_id)
    analyzed = analyze_sentiment(comments)

    df = pd.DataFrame(analyzed)
    summary = df['sentiment'].value_counts().to_dict()
    return render_template("result.html", comments=analyzed, summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
