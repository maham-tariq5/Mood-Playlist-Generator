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
