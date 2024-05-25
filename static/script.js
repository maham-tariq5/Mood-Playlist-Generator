// Handle the form submission for fetching recommendations
document.getElementById('moodForm').onsubmit = function(event) {
    event.preventDefault(); // Prevent the default form submission
    showSpinner(); // Show spinner when request starts

    // Get mood and number of songs from form inputs
    var moods = document.getElementById('moods').value;
    var numSongs = document.getElementById('numSongs').value;

    // Fetch recommendations from the server
    fetch(`/recommendations?moods=${moods}&numSongs=${numSongs}`)
        .then(response => {
            hideSpinner(); // Hide spinner when data is received

            // Handle unauthorized response by redirecting to the login page
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = ''; // Clear previous content

            // Display an error message if there's an error in the response
            if (data.error) {
                recommendationsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                return;
            }

            // Add a button to save the playlist
            const savePlaylistButton = document.createElement('button');
            savePlaylistButton.textContent = 'Save as Playlist';
            savePlaylistButton.onclick = function() {
                savePlaylist(moods, data, numSongs); // Call savePlaylist function
            };
            recommendationsDiv.appendChild(savePlaylistButton);

            // Display each recommended track
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

// Show loading spinner
function showSpinner() {
    document.getElementById('loadingSpinner').hidden = false;
}

// Hide loading spinner
function hideSpinner() {
    document.getElementById('loadingSpinner').hidden = true;
}

// Save the playlist to the user's Spotify account
function savePlaylist(mood, tracks, numSongs) {
    const trackUris = tracks.map(track => track.uri); // Get track URIs from the tracks array

    // Send a request to create a playlist with the recommended tracks
    fetch(`/create_playlist?mood=${mood}&numSongs=${numSongs}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tracks: trackUris }) // Send track URIs in the request body
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Show a message when the playlist is created successfully
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save playlist.'); // Show an error message if playlist creation fails
    });
}
