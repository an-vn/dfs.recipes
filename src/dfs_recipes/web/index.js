import './styles/normalize.css';
import './styles/index.css';
import {
    AllCommunityModule,
    ModuleRegistry,
    themeBalham,
    iconSetMaterial,
    provideGlobalGridOptions
} from 'ag-grid-community';
import {
    navigation,
    eventBus,
    LinesContainer,
    DataContainer,
    MessageContainer,
    ChartContainer,
    LLMOutputContainer
} from './modules/navigation.js';
import { Lines } from './modules/lines.js';
import { Data } from './modules/Data.js';
import { Chart } from './modules/chart.js';
import { Message } from './modules/message.js';
import { spawnSandboxWorker } from './modules/sandbox';

ModuleRegistry.registerModules([AllCommunityModule]);

provideGlobalGridOptions({
    theme: themeBalham.withPart(iconSetMaterial),
    defaultColDef: {
        sortable: true,
        resizable: true,
        filter: true,
        floatingFilter: true,
        minWidth: 60,
        flex: 1,
    },
    suppressCellFocus: true,
    enableCellSpan: true,
}, 'deep');

document.addEventListener('DOMContentLoaded', async function () {

    if (!window.Worker) {
        alert('Your browser does not support Web Workers. Please use a modern browser to access this application.');
        return;
    }

    await fetch('/api/session').then((res) => {
        console.log(res);
    });

    const chart = new Chart(ChartContainer, LLMOutputContainer);
    const data = new Data(DataContainer);
    const lines = new Lines(LinesContainer, data);
    const message = new Message(MessageContainer, data, chart);

    LinesContainer.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'nearest'
    });

    navigation.subscribe(lines);
    navigation.subscribe(data);
    navigation.subscribe(chart);
    navigation.subscribe(message);
});


const overlay = document.querySelector('#loadOverlay');
setTimeout(() => {
    overlay.style.opacity = '0';
    overlay.style.visibility = 'hidden';
    overlay.style.zIndex = '-1';
}, 100);
