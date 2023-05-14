const RECAPTCHA_SITE_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI";
const EMPTY_TOKEN = "";

async function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function pollResponse() {
    return new Promise(async resolve => {
        let token = EMPTY_TOKEN;
        while (token === EMPTY_TOKEN || token === undefined) {
            await sleep(100);
            token = $('[name="g-recaptcha-response"]').val();
        }
        resolve(token);
    });
}

function callRecaptcha(actionName, callback) {
    console.log(`callRecaptcha called`);
    grecaptcha.ready(() => {
        console.log(`grecaptcha is ready`);
        grecaptcha.execute(RECAPTCHA_SITE_KEY, {action: actionName}).then(async () => {
            console.log(`grecaptcha.execute done`);
            const token = await pollResponse();
            callback(token);
        });
    });
}
