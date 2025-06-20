import { Observable } from './observable.js';

const header = document.querySelector('#header');
const footer = document.querySelector('footer');

const LinesContainer = document.querySelector('#LinesContainer');
const DataContainer = document.querySelector('#DataContainer');
const MessageContainer = document.querySelector('#MessageContainer');
const ChartContainer = document.querySelector('#ChartContainer');
const LLMOutputContainer = document.querySelector('#LLMOutputContainer');
const radioButtons = document.querySelectorAll('input[type="radio"]');

const containers = {
    lines: LinesContainer,
    data: DataContainer,
    message: MessageContainer,
    chart: ChartContainer,
    llmOutput: LLMOutputContainer,
};

const eventBus = new EventTarget();

const navigation = new Observable();

radioButtons.forEach(radio => {
    radio.addEventListener('change', function () {
        // eventBus.dispatchEvent(new CustomEvent('radioChange', { detail: { value: this.value } }));
        navigation.notify(this.value);

        containers[this.value].scrollIntoView({
            behavior: 'smooth',
            block: 'center',
            inline: 'nearest'
        });
    });
});

let lastActiveContainer = 'lines';
let hasChart = false;

for (const [key, container] of Object.entries(containers)) {
    if (key === 'lines') {
        continue;
    }
    container.addEventListener('click', function (e) {
        // FIXME
        navigation.notify(key);
        container.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
            inline: 'center',
        });

        return;

        console.log({ lastActiveContainer, key, hasChart });

        if (!hasChart && key === 'chart') {
            hasChart = true;
        }

        if (lastActiveContainer === 'chart' && key === 'data') {
            LinesContainer.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'start',
            });
        } else if (lastActiveContainer === 'data' && key === 'data') {

        } else if (lastActiveContainer === 'lines' && key === 'data') {

        } else if (hasChart && key === 'data') {
            navigation.notify(key);
            container.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center',
            });
        }
        lastActiveContainer = key;
    });
}

export {
    navigation,
    eventBus,
    LinesContainer,
    DataContainer,
    MessageContainer,
    ChartContainer,
    LLMOutputContainer,
};

