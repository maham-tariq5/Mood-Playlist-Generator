document.getElementById('moodForm').onsubmit = function(event) {
    event.preventDefault();
    var moods = document.getElementById('moods').value;
    fetch(`/recommendations?moods=${moods}`)
        .then(response => {
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
                savePlaylist(moods, data);
            };
            recommendationsDiv.appendChild(savePlaylistButton);

            data.forEach(track => {
                const trackDiv = document.createElement('div');
                trackDiv.innerHTML = `Track: ${track.track} - Artist: ${track.artist} - Album: ${track.album} - <a href="${track.link}" target="_blank">Listen on Spotify</a>`;
                recommendationsDiv.appendChild(trackDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('recommendations').innerHTML = `<p>An error occurred while fetching recommendations.</p>`;
        });
};

function savePlaylist(mood, tracks) {
    const trackUris = tracks.map(track => track.uri);
    fetch(`/create_playlist?mood=${mood}`, {
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
