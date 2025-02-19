const STATUS_URL = "http://localhost:8000/status?process_id=" + PROCESSID;
console.log(STATUS_URL);
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
            console.log(data);
            if (data.ready) {
                var audio = GENERATED_URL + "?process_id=" + PROCESSID
                console.log(audio)
                window.location.href = audio;
            } else {
                setTimeout(pollStatus, 3000);
            }
        })
        .catch(err => {
            var audio = GENERATED_URL + "?wav_file=" + PROCESSID + "/wav_file.wav" + "&bmp_file=" + PROCESSID + "/bmp_file.bmp"
            console.log(audio)
            console.log(err);
            let errorCode = err.code || 0;
            // window.location.href = ERROR_URL + "?code=" + errorCode;
        });
};
pollStatus();