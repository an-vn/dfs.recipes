import { Observable } from './observable.js';

const header = document.querySelector('#header');
const footer = document.querySelector('footer');
const grid = document.querySelector('.grid');

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

let lastActive = 'lines';
let hasChart = false;

for (const [key, container] of Object.entries(containers)) {
    container.addEventListener('click', function (e) {
        // console.log('Clicked on:', key);
        // e.preventDefault();
        // e.stopPropagation();

        let inline = 'center';

        // console.log({lastActive, hasChart, key});

        switch (key) {
            case 'lines':
                inline = 'start';
                break;
            case 'data':
            case 'message':
                inline = hasChart ? 'center' : 'nearest';
                grid.style.gridTemplateColumns = '300px 80vw 60vw';
                break;
            case 'chart':
            case 'llmOutput':
                inline = 'end';
                hasChart = true;
                grid.style.gridTemplateColumns = '300px 40vw 60vw';
                break;
        }

        container.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
            inline,
        });

        // navigation.notify(key);
        lastActive = key;
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

