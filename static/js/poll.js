const STATUS_URL = "http://13.64.211.233/status?process_id=" + PROCESSID;
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
            if (data.ready) {
                window.location.href = GENERATED_URL + "?process_id=" + PROCESSID;
            } else {
                setTimeout(pollStatus, 3000);
            }
        })
        .catch(err => {
            console.log(err);
            let errorCode = err.code || 0;
            // window.location.href = ERROR_URL + "?code=" + errorCode;
        });
};
pollStatus();