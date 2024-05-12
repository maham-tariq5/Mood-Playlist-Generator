from flask import Flask, jsonify, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)
app.secret_key = 'SOME_SECRET_KEY'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Set your Spotify API credentials
CLIENT_ID = 'e859674243c8458f8814372e0ca9672b'
CLIENT_SECRET = '3edc0de852f64317b2142d6a6262696e'
REDIRECT_URI = 'http://localhost:3000'  # Ensure this matches your registered URI on the Spotify dashboard
SCOPE = 'user-library-modify playlist-modify-private'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index', _external=True))

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    moods = request.args.get('moods', 'happy, sad, angry, relaxed, energetic, euphoric')
    if not moods:
        return jsonify({'error': 'No moods provided'}), 400

    mood_genre_map = {
        'happy': 'pop',
        'sad': 'r-n-b',
        'angry': 'metal',
        'relaxed': 'indie-pop',
        'energetic': 'hip-hop',
        'euphoric': 'electronic'
    }
    
    genres = [mood_genre_map[mood.strip().lower()] for mood in moods.split(',') if mood.strip().lower() in mood_genre_map]
    if not genres:
        return jsonify({'error': 'Invalid moods'}), 400

    sp = create_spotify_client()
    if sp is None:
        # Return a JSON response indicating the need to log in instead of redirecting
        return jsonify({'error': 'Authentication required', 'login_required': True}), 401

    try:
        results = sp.recommendations(seed_genres=genres, limit=10)
        tracks = [{
            'track': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'link': track['external_urls']['spotify']
        } for track in results['tracks']]
        return jsonify(tracks)
    except spotipy.exceptions.SpotifyException as e:
        return jsonify({'error': str(e)}), 500





@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    sp = create_spotify_client()
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, 'Mood Based Playlist', public=False)
    track_uris = request.json['tracks']
    sp.playlist_add_items(playlist['id'], track_uris)
    return jsonify({'message': 'Playlist created successfully!', 'playlist_id': playlist['id']})

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,  # Make sure the redirect URI exactly matches the one registered in your Spotify app settings
        scope=SCOPE,
        show_dialog=True,
        cache_path="token_info"
    )

def create_spotify_client():
    token_info = session.get('token_info', None)
    if not token_info:
        # Redirect to login if there is no token
        print("Token info not found in session, redirecting to login.")
        return None  # Returning None to indicate that the client could not be created

    if spotipy.oauth2.is_token_expired(token_info):
        sp_oauth = create_spotify_oauth()
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info  # Update the session with the new token
        except spotipy.SpotifyException as e:
            print("Failed to refresh token:", str(e))
            return None

    return spotipy.Spotify(auth=token_info['access_token'])



if __name__ == '__main__':
    app.run(debug=True, port=3000)

