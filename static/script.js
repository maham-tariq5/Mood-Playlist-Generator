document.getElementById('moodForm').onsubmit = function(event) {
    event.preventDefault();
    showSpinner(); // Show spinner when request starts
    var moods = document.getElementById('moods').value;
    var numSongs = document.getElementById('numSongs').value;

    fetch(`/recommendations?moods=${moods}&numSongs=${numSongs}`)
        .then(response => {
            hideSpinner(); // Hide spinner when data is received
            if (!response.ok) {
                if (response.status === 401) {
                    // Handle 401 Unauthorized response by redirecting to the login page
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = '';  // Clear previous content
            if (data.error) {
                recommendationsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                return;
            }

            // Add a button to save the playlist
            const savePlaylistButton = document.createElement('button');
            savePlaylistButton.textContent = 'Save as Playlist';
            savePlaylistButton.onclick = function() {
                savePlaylist(moods, data, numSongs);
            };
            recommendationsDiv.appendChild(savePlaylistButton);

            data.forEach(track => {
                const trackDiv = document.createElement('div');
                trackDiv.innerHTML = `Track: ${track.track} - Artist: ${track.artist} - Album: ${track.album} - <a href="${track.link}" target="_blank">Listen on Spotify</a>`;
                recommendationsDiv.appendChild(trackDiv);
            });
        })
        .catch(error => {
            hideSpinner(); // Ensure spinner is hidden on error
            console.error('Error:', error);
            document.getElementById('recommendations').innerHTML = `<p>An error occurred while fetching recommendations.</p>`;
        });
};

function showSpinner() {
    document.getElementById('loadingSpinner').hidden = false;
}

function hideSpinner() {
    document.getElementById('loadingSpinner').hidden = true;
}

function savePlaylist(mood, tracks, numSongs) {
    const trackUris = tracks.map(track => track.uri);
    fetch(`/create_playlist?mood=${mood}&numSongs=${numSongs}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tracks: trackUris })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save playlist.');
    });
}
