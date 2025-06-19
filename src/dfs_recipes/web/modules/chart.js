import * as echarts from 'echarts';
import 'echarts-gl';
import { spawnSandboxWorker } from './sandbox';

export class Chart {
    constructor(container, llmOutput) {
        this.container = container;
        this.llmOutput = llmOutput;
        this.eChartsInstance = null;
        this.initChartInstance();
        window.onresize = this.handleResize.bind(this);
        this.loadingParams = {
            color: 'rgba(0, 0, 0, 0.5)',
            fontSize: 13,
        };

        // this.chartError = document.querySelector('.chart-error');
    }

    initChartInstance() {
        if ((!this.eChartsInstance) || this.eChartsInstance.isDisposed()) {
            const chartElement = document.createElement('div');
            chartElement.classList.add('chart');
            this.container.appendChild(chartElement);

            this.eChartsInstance = echarts.init(chartElement, 'vintage', {
                useDirtyRect: true,
            });
        }
    }

    handleResize() {
        if (this.eChartsInstance) {
            this.eChartsInstance.resize();
        }
    }

    async createChart(message, dataset) {
        this.llmOutput.innerHTML = '';
        this.eChartsInstance.clear();
        this.eChartsInstance.showLoading(this.loadingParams);
        this.llmOutput.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
            inline: 'center'
        });

        await fetch('/api/chart', {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                dataset,
            }),
        })
            .then((res) => {
                if (!res.ok) throw new Error(`[${res.status}] ${res.statusText}`);
                return res.json();
            })
            .then((res) => {
                const { chart_title, chart_type, javascript, explanation } = res;

                const worker = spawnSandboxWorker(javascript);
                worker.postMessage(dataset);
                worker.onmessage = (e) => {
                    const { options, error } = e.data;
                    if (error) {

                    } else {
                        this.eChartsInstance.setOption(options, true);
                        this.llmOutput.innerHTML = `<pre><strong>${chart_title}</strong><br>${explanation}</pre>`;
                    }
                };
            })
            .catch((e) => {
                console.error(e);
                this.llmOutput.innerHTML = 'ERROR: AI-generated content may contain errors & is not guaranteed to be fully accurate';
                this.eChartsInstance.getDom().remove();
                this.eChartsInstance.dispose();
                this.initChartInstance();
            })
            .finally(() => {
                this.eChartsInstance.hideLoading();
            });
    }

    initCallback(threadId, version) {
        const eventSource = new EventSource(`/events/${threadId}/${version}`);
        eventSource.onopen = () => {
            console.log('EventSource connection opened');
        };
        eventSource.addEventListener('callback', ({ data }) => {
            const chart = JSON.parse(data);
            console.log('Received callback:', chart);
            if (chart.complete) {
                // renderChart();
                console.log(chart);
            }
        });

        eventSource.onerror = (e) => {
            eventSource.close();
        };
    }

    handleNotify(data) {
    }
}







