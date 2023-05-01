from flask import Flask, request, redirect, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from urllib.parse import quote_plus, unquote_plus
import os

def loadDataFrame(language, genre, listeners, letter):
    formatted_genre = genreFormatter(language, genre)
    popularity = popularityCalculator(listeners)
    raw_artist_df = pd.read_csv("artists.csv")
    filtered_df = raw_artist_df[raw_artist_df["genres"].str.contains(formatted_genre)]
    filtered_df = filtered_df.loc[filtered_df["popularity"].between(popularity - 10, popularity + 10)]
    filtered_df = filtered_df.loc[filtered_df["name"].str.startswith(letter)]
    
    return filtered_df

def loadSpotifyAPI():
    cid = os.environ.get("SPOTIFY_CLIENT_ID")
    secret = os.environ.get("SPOTIFY_SECRET")
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return sp

def popularityCalculator(amount):
    popularity = 0
    if 1000 <= amount < 5000:
        popularity = 5
    elif 5000 <= amount < 10000:
        popularity = 15
    elif 10000 <= amount < 50000:
        popularity = 25
    elif 50000 <= amount < 100000:
        popularity = 35
    elif 100000 <= amount < 500000:
        popularity = 45
    elif 500000 <= amount < 1000000:
        popularity = 55
    elif 1000000 <= amount < 5000000:
        popularity = 65
    elif 5000000 <= amount < 10000000:
        popularity = 75
    elif 10000000 <= amount < 50000000:
        popularity = 85
    elif 50000000 <= amount <= 100000000:
        popularity = 95

    return popularity

def genreFormatter(language, genre):
    if not language and not genre:
        return ("")
    
    return (language + " " + genre).lower().strip()

def albumsValidator(sp, artist_id, album_count):
    album_count_real = 0
    curr_album_name = ""
    many_albums = False
    if album_count >= 15:
        many_albums = True
    search_results = sp.artist_albums(artist_id=artist_id, album_type="album", limit=50)
    
    for i, t in enumerate(search_results["items"]):
        if search_results["items"][i]["name"] != curr_album_name:
            album_count_real += 1
        curr_album_name = search_results["items"][i]["name"]

    if many_albums and album_count_real >= 15:
        return True
    elif not many_albums and album_count <= album_count_real <= album_count + 1:
        return True
    
    return False

def topSongPopularityCalculator():
    pass

def initialSearch(sp, genre, year):
    batch_results = []
    for i in range(0, 1000, 50):
        search_results = sp.search(q=genre + "year: " + year, type="artist", limit=50, offset=i)
        for i, t in enumerate(search_results["artists"]["items"]):
            batch_results.append([t["name"], t["popularity"], t["id"]])
    
    return batch_results

def continuousPrompter(sp, artists):
    prompt_list = [["amountOfAlbumsRequest", "albumsValidator"]]
    amount = amountOfAlbumsRequest()
    
    for i, row in artists.iterrows():
        artist = row["id"]
        if not albumsValidator(sp, artist, amount):
            artists = artists.drop(i)

    return artists["name"].values[0], artists["id"].values[0]    

def getArtistImage(sp, artist_id):
    artist = sp.artist(artist_id)
    image = artist["images"][0]["url"]

    return image

def popularityRequest():
    return int(request.form.get("popularity"))

def amountOfAlbumsRequest():
    return int(request.form.get("album_count"))

def popularityOfTopSongRequest():
    return int(request.form.get("top_song_popularity"))

def languageRequest():
    return request.form.get("language")

def genreRequest():
    return request.form.get("genre")

def firstReleaseRequest():
    return request.form.get("first_release")

def firstLetterRequest():
    return request.form.get("first_letter")

def main():
    sp = loadSpotifyAPI()
    chosen_language = languageRequest()
    chosen_genre = genreRequest()
    monthly_listeners = popularityRequest()
    first_letter = firstLetterRequest()
    artist_df = loadDataFrame(chosen_language, chosen_genre, monthly_listeners, first_letter)
    artist, id = continuousPrompter(sp, artist_df)
    image_url = getArtistImage(sp, id)

    return artist, image_url

app = Flask(__name__, static_folder="static")

@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        artist, image = main()
        return redirect(url_for("result", artist=artist, image=quote_plus(image)))
    else:
        return render_template("index.html")
    
@app.route("/result/<artist>/<path:image>")
def result(artist, image):
    decoded_image = unquote_plus(image)
    return render_template("results.html", artist=artist, image=decoded_image)

if __name__ == "__main__":
    app.run()
