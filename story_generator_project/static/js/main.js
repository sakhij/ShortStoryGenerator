document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('story-form');
    const submitBtn = document.getElementById('generate-btn');
    
    if (form && submitBtn) {
        form.addEventListener('submit', function() {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Story...';
            
            const loadingAlert = document.createElement('div');
            loadingAlert.className = 'alert alert-info mt-3';
            loadingAlert.innerHTML = '<i class="fas fa-magic"></i> Creating your story... This may take up to 3 minutes.';
            form.appendChild(loadingAlert);
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            new bootstrap.Alert(alert).close();
        }, 5000);
    });
});
let mediaRecorder;
let recordedChunks = [];
let recordingTimer;
let recordingStartTime;

function toggleInputFields() {
    const inputType = document.querySelector('input[name="input_type"]:checked').value;
    const textSection = document.getElementById('text-prompt-section');
    const audioSection = document.getElementById('audio-upload-section');
    const generateBtn = document.getElementById('generate-btn-text');

    // Show/hide sections based on input type
    if (inputType === 'text') {
        textSection.style.display = 'block';
        audioSection.style.display = 'none';
        generateBtn.textContent = 'Generate Story from Text';
    } else if (inputType === 'audio') {
        textSection.style.display = 'none';
        audioSection.style.display = 'block';
        generateBtn.textContent = 'Generate Story from Audio';
    } else { // both
        textSection.style.display = 'block';
        audioSection.style.display = 'block';
        generateBtn.textContent = 'Generate Story from Text + Audio';
    }
}

async function toggleRecording() {
    const recordBtn = document.getElementById('record-btn');
    const recordingControls = document.getElementById('recording-controls');

    try {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
            // Start recording
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            recordedChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Show preview
                const audioPlayer = document.getElementById('audio-player');
                audioPlayer.src = audioUrl;
                document.getElementById('audio-preview').style.display = 'block';
                
                // Store the blob for later use
                audioPlayer.recordedBlob = audioBlob;
            };

            mediaRecorder.start();
            recordBtn.style.display = 'none';
            recordingControls.style.display = 'block';
            
            // Start timer
            recordingStartTime = Date.now();
            recordingTimer = setInterval(updateRecordingTimer, 100);

        }
    } catch (error) {
        alert('Error accessing microphone: ' + error.message);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        document.getElementById('record-btn').style.display = 'inline-block';
        document.getElementById('recording-controls').style.display = 'none';
        
        clearInterval(recordingTimer);
    }
}

function updateRecordingTimer() {
    const elapsed = (Date.now() - recordingStartTime) / 1000;
    const minutes = Math.floor(elapsed / 60);
    const seconds = Math.floor(elapsed % 60);
    document.getElementById('recording-timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function useRecording() {
    const audioPlayer = document.getElementById('audio-player');
    const audioInput = document.getElementById('audio-upload');
    
    if (audioPlayer.recordedBlob) {
        // Create a File object from the blob
        const file = new File([audioPlayer.recordedBlob], 'recording.wav', { type: 'audio/wav' });
        
        // Create a new FileList (this is a bit hacky but works)
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        audioInput.files = dataTransfer.files;
        
        // Hide preview
        document.getElementById('audio-preview').style.display = 'none';
    }
}

function discardRecording() {
    document.getElementById('audio-preview').style.display = 'none';
    document.getElementById('audio-player').src = '';
}

// Initialize the form state on page load
document.addEventListener('DOMContentLoaded', function() {
    toggleInputFields();
});