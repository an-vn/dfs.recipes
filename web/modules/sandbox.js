export function spawnSandboxWorker(appCode) {
    appCode = `${appCode}
onmessage = (e) => {
    try {
        const options = JSON.stringify(createChartOptions(e.data));
        postMessage({ options: JSON.parse(options) });
    } catch (e) {
        postMessage({ error: e.message });
    }
};
`
    const blob = new Blob([appCode]);
    return new Worker(window.URL.createObjectURL(blob));
}
