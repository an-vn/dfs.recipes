onmessage = (e) => {
    try {
        const options = JSON.stringify(createChartOptions(e.data));
        postMessage({ options: JSON.parse(options) });
    } catch (e) {
        postMessage({ error: e.message });
    }
};
