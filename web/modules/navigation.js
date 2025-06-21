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

let lastActive = 'lines';

for (const [key, container] of Object.entries(containers)) {
    container.addEventListener('click', function (e) {

        let inline = 'center';

        switch (key) {
            case 'lines':
                inline = 'start';
                break;
            case 'chart':
            case 'llmOutput':
                inline = 'end';
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

