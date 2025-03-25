let mediaRecorder;
let audioChunks = [];
let lastText = "";

document.getElementById('record').addEventListener('click', async () => {
    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        let audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        let formData = new FormData();
        formData.append('audio', audioBlob, 'recorded.wav');
        formData.append('lang_from', document.getElementById('lang_from').value);
        formData.append('lang_to', document.getElementById('lang_to').value);

        let response = await fetch('/translate', { method: 'POST', body: formData });
        let data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            lastText = data.original_text;
            document.getElementById('original_text').innerText = data.original_text;
            document.getElementById('translated_text').innerText = data.translated_text;
            document.getElementById('audio_player').src = data.audio_url;
        }
    };

    mediaRecorder.start();
    audioChunks = [];
    document.getElementById('record').disabled = true;
    document.getElementById('stop').disabled = false;
});

document.getElementById('stop').addEventListener('click', () => {
    mediaRecorder.stop();
    document.getElementById('record').disabled = false;
    document.getElementById('stop').disabled = true;
});

document.getElementById('retranslate').addEventListener('click', async () => {
    let response = await fetch('/retranslate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: lastText, lang_to: document.getElementById('lang_to').value })
    });

    let data = await response.json();
    document.getElementById('translated_text').innerText = data.translated_text;
    document.getElementById('audio_player').src = data.audio_url;
});
