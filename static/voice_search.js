
document.addEventListener('DOMContentLoaded', function() {
    const voiceSearchButton = document.getElementById('voiceSearchButton');

    voiceSearchButton.addEventListener('click', function() {
        // Check if the browser supports Web Speech API
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                const word = event.results[0][0].transcript.trim(); // Get the recognized word and remove leading/trailing spaces
                window.location.href = `/result/${word}`;
            };

            recognition.onerror = function(event) {
                console.error('Speech recognition error: ', event.error);
                alert('Error occurred in recognition: ' + event.error);
            };

            recognition.start(); // Start speech recognition
        } else {
            console.error('Web Speech API not supported');
            alert('Web Speech API is not supported in this browser');
        }
    });
});
