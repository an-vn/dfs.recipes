const webauthnUser = document.querySelector('#webauthn-user');
const authenticateButton = document.querySelector('#authenticate');
const registerButton = document.querySelector('#register');

const asArrayBuffer = v => Uint8Array.from(atob(v.replace(/_/g, '/').replace(/-/g, '+')), c => c.charCodeAt(0));
const asBase64 = (v) => btoa(String.fromCharCode(...new Uint8Array(v)));

async function fetchPublicKey(path) {
    const res = await fetch(`/api/${path}`, {
        mode: 'cors',
        credentials: 'include',
    });
    if (!res.ok) {
        throw new Error(`Unexpected response ${res.status}: ${await res.text()}`);
    }
    return await res.json();
}

async function post(path, creds) {
    const { attestationObject, clientDataJSON, signature, authenticatorData } = creds.response;

    const data = {
        id: creds.id,
        rawId: asBase64(creds.rawId),
        response: {
            attestationObject: asBase64(attestationObject),
            clientDataJSON: asBase64(clientDataJSON),
        }
    };
    if (signature) {
        data.response.signature = asBase64(signature);
        data.response.authenticatorData = asBase64(authenticatorData);
    }
    const res = await fetch(`/api/${path}`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'content-type': 'application/json' }
    });
    if (!res.ok) {
        throw new Error(`Unexpected response ${res.status}: ${await res.text()}`);
    }
}

async function register() {
    const path = `register/${document.getElementById('username').value}`;
    const publicKey = await fetchPublicKey(path);
    publicKey.user.id = asArrayBuffer(publicKey.user.id);
    publicKey.challenge = asArrayBuffer(publicKey.challenge);
    const creds = await navigator.credentials.create({ publicKey });
    await post(path, creds);
}

async function authenticate() {
    const publicKey = await fetchPublicKey('auth');
    publicKey.challenge = asArrayBuffer(publicKey.challenge);
    publicKey.allowCredentials[0].id = asArrayBuffer(publicKey.allowCredentials[0].id);
    delete publicKey.allowCredentials[0].transports;
    const creds = await navigator.credentials.get({ publicKey });
    await post('auth', creds);
}

authenticateButton.onclick = authenticate;
registerButton.onclick = register;

fetch(`/api/login`, {
    mode: 'cors',
    credentials: 'include',
})
    .then((res) => {
        if (res.ok) {
            return res.json();
        } else {
            throw new Error(`Unexpected response ${res.status}: ${res.statusText}`);
        }
    })
    .then((data) => {
        webauthnUser.textContent = data.username;
        return authenticate();
    })
    .catch((e) => {
        registerButton.style.display = 'block';
    });
