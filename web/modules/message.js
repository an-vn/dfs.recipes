export class Message {
    constructor(container, data, chart) {
        this.container = container;
        this.messageInput = document.querySelector('#message-input');
        this.messageSend = document.querySelector('#message-send');
        this.data = data;
        this.chart = chart;
        window.addEventListener('keydown', this.handleKeyDown.bind(this));
        this.messageSend.onclick = this.send.bind(this);
    }

    toggle() {
        this.container.click();
    }

    async handleKeyDown(e) {
        if (e.ctrlKey || e.metaKey) {
            e.stopPropagation();

            if (e.key === 'Enter') {
                e.preventDefault();
                await this.send();
            }

            if (e.key === 'k') {
                e.preventDefault();
                this.toggle();
            }
        }
    }

    async send(e) {
        // e.preventDefault();
        // e.stopPropagation();

        if (!this.messageInput.value.trim()) {
            return;
        }

        this.chart.llmOutputContainer.click();

        this.chart.createChart(this.messageInput.value, this.data.getRowData())
            .then(() => {
                this.messageInput.value = '';
            });
    }

    async chat() {
        const controller = new AbortController();

        const res = await fetch('/api/message', {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: this.messageInput.value,
            }),
            signal: controller.signal
        });

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        if (res.body) {
            const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();

            while (true) {
                const {done, value} = await reader.read();

                if (done) break;

                // this.chatOutput.innerHTML += value;
            }
        }

        this.messageInput.value = '';
    }

    async getHistory() {
        return fetch('/api/history', {
            mode: 'cors',
            credentials: 'include',
        })
            .then(res => {
                if (!res.ok) throw new Error(`[${res.status}] ${res.statusText}`);
                return res.json();
            })
            .catch(error => {
                console.error('Error fetching game log data:', error);
            });

    }

    handleNotify(data) {}
}
