let poll_count = 0;
const maxPolls = 20;
const pollStatus = () => {
    if (poll_count >= maxPolls) {
        window.location.href = ERROR_URL + "?code=0";
        return;
    }
    poll_count++;
    fetch(STATUS_URL)
        .then(response => response.json())
        .then(data => {
            if (data.ready) {
                window.location.href = GENERATED_URL + "?wav_file=" + data.wav_file + "&bmp_file=" + data.bmp_file;
            } else {
                setTimeout(pollStatus, 3000);
            }
        })
        .catch(err => {
            let errorCode = err.code || 0;
            window.location.href = ERROR_URL + "?code=" + errorCode;
        });
};
pollStatus();