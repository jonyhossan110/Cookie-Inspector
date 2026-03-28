
    document.addEventListener("DOMContentLoaded", function() {
        var audio = document.getElementById("my_bg_audio");
        var controls = document.getElementById("audio_controls");
        var btnPlay = document.getElementById("btn_play");
        var btnPause = document.getElementById("btn_pause");
        var btnRemove = document.getElementById("btn_remove");

        // Storage Keys
        var timeKey = "site_audio_timestamp"; 
        var removedKey = "site_audio_removed"; 

        // 1. Check if user previously "Removed" the player. If so, do nothing.
        if (localStorage.getItem(removedKey) === "true") {
            return; // Stop script execution
        }

        // 2. Show the controls since user hasn't removed them
        controls.style.display = "flex";

        // 3. Set Volume to 30%
        audio.volume = 0.3;

        // 4. Handle Time (Resume vs Start at 30s)
        var savedTime = localStorage.getItem(timeKey);
        if (savedTime) {
            audio.currentTime = parseFloat(savedTime);
        } else {
            audio.currentTime = 30; // Start at 30s for new visitors
        }

        // 5. Play Logic
        function startPlayback() {
            var playPromise = audio.play();
            if (playPromise !== undefined) {
                playPromise.then(_ => {
                    // Update UI to show Pause button
                    btnPlay.style.display = "none";
                    btnPause.style.display = "inline-block";
                })
                .catch(error => {
                    console.log("Autoplay blocked. Waiting for click.");
                });
            }
        }

        // Try to play automatically
        startPlayback();

        // Also try to play on first interaction (if autoplay was blocked)
        document.body.addEventListener('click', function() {
            if (audio.paused) {
                startPlayback();
            }
        }, { once: true });

        // 6. Button Actions
        btnPlay.addEventListener('click', function() {
            audio.play();
            btnPlay.style.display = "none";
            btnPause.style.display = "inline-block";
        });

        btnPause.addEventListener('click', function() {
            audio.pause();
            btnPause.style.display = "none";
            btnPlay.style.display = "inline-block";
        });

        btnRemove.addEventListener('click', function() {
            audio.pause();
            controls.style.display = "none"; // Hide controls
            localStorage.setItem(removedKey, "true"); // Remember this preference
            localStorage.removeItem(timeKey); // Clear time memory
        });

        // 7. Save Time Loop
        audio.addEventListener('timeupdate', function() {
            localStorage.setItem(timeKey, audio.currentTime);
        });
    });
    