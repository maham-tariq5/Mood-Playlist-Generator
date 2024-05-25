from flask import Flask, jsonify, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'SOME_SECRET_KEY'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Setting API credentials
CLIENT_ID = 'e859674243c8458f8814372e0ca9672b'
CLIENT_SECRET = '3edc0de852f64317b2142d6a6262696e'
REDIRECT_URI = 'http://localhost:3000/callback'
SCOPE = 'user-library-modify playlist-modify-private'

@app.route('/')
def index():
    return render_template('index.html') # rendering home page

@app.route('/login')
def login():
    # getting user to plug in spotify account credentials
    sp_oauth = create_spotify_oauth() 
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # redirecting back to web page after authentication
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index', _external=True))

@app.route('/recommendations', methods=['GET'])
def recommendations():
    # get request to server to get the user's mood choice
    moods = request.args.get('moods', 'happy, sad, angry, relaxed, energetic, euphoric')
    num_songs = int(request.args.get('numSongs', 10))
    if not moods:
        return jsonify({'error': 'No moods provided'}), 400

    # predefined genres mapped with moods
    mood_genre_map = {
        'happy': 'pop', 'sad': 'r-n-b', 'angry': 'metal',
        'relaxed': 'indie-pop', 'energetic': 'hip-hop', 'euphoric': 'electronic'
    }

    genre = mood_genre_map.get(moods.strip().lower())
    if not genre:
        return jsonify({'error': 'Invalid mood'}), 400

    sp = create_spotify_client()
    if sp is None:
        return jsonify({'error': 'Authentication required'}), 401

    tracks, error = get_recommendations_by_genre(sp, genre, num_songs)
    if error:
        return jsonify({'error': error}), 500

    track_info = [{
        'track': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'link': track['external_urls']['spotify'],
        'uri': track['uri']
    } for track in tracks]

    # Store only the URIs in the session 
    session['recommended_track_uris'] = [track['uri'] for track in tracks]
    return jsonify(track_info)

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # post request creating playlist from songs recommanded
    mood = request.args.get('mood')
    if not mood:
        return jsonify({'error': 'Mood parameter is missing'}), 400

    if 'recommended_track_uris' not in session or not session['recommended_track_uris']:
        return jsonify({'error': 'No track URIs available for playlist creation'}), 400

    track_uris = session['recommended_track_uris']

    sp = create_spotify_client()
    if sp is None:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, f'{mood.title()} Mood Playlist', public=False)
        sp.playlist_add_items(playlist['id'], track_uris)
        return jsonify({'message': 'Playlist created successfully!', 'playlist_id': playlist['id']})
    except spotipy.exceptions.SpotifyException as e:
        return jsonify({'error': str(e)}), 500

def get_recommendations_by_genre(sp, genre, num_songs):

    # Get recommendations from Spotify based on genre
    try:
        results = sp.recommendations(seed_genres=[genre], limit=num_songs)
        return results['tracks'], None
    except spotipy.exceptions.SpotifyException as e:
        return None, str(e)

def create_spotify_oauth():
   # Create a SpotifyOAuth object for handling OAuth
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_path="token_info"
    )

def create_spotify_client():
    # Create a Spotify client using the stored token information
    token_info = session.get('token_info', None)
    if not token_info:
        print("Token info not found in session, redirecting to login.")
        return None

    sp_oauth = create_spotify_oauth()
    if sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        except spotipy.SpotifyException as e:
            print("Failed to refresh token:", str(e))
            return None

    return spotipy.Spotify(auth=token_info['access_token'])

if __name__ == '__main__':
    app.run(debug=True, port=3000)
