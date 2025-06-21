import { createGrid } from 'ag-grid-community';
import { LinesContainer, eventBus } from './navigation';

export class Lines {
    #gridApi;

    constructor(container, data) {
        this.onSelectionChanged = this.onSelectionChanged.bind(this);
        this.loadTable = this.loadTable.bind(this);
        this.loadLines = this.loadLines.bind(this);
        this.data = data;
        this.container = container;
        this.defaultGridOptions = {
            rowSelection: {
                mode: 'singleRow',
                checkboxes: false,
                enableClickSelection: 'enableSelection',
            },
            onFirstDataRendered(p) {
                p.api.getDisplayedRowAtIndex(0).setSelected(true);
            },
            onSelectionChanged: this.onSelectionChanged
        };

        this.loadLines().then((gridOptions) => {
            this.#gridApi = createGrid(this.container, {
                ...gridOptions,
                ...this.defaultGridOptions,
            });
        });
    }

    onSelectionChanged(event) {
        const { LEAGUE, TEAM, PLAYER } = event.api.getSelectedRows()[0];
        this.loadTable(LEAGUE, TEAM, PLAYER)
            .then((res) => {
                this.data.setTableData(res);
            });
    }

    loadTable(league, team, player) {
        return fetch(`/data/${league}/${team}/${player}.json`)
            .then(res => {
                if (!res.ok) throw new Error(`[${res.status}] ${res.statusText}`);
                return res.json();
            })
            .catch(error => {
                console.error('Error fetching game log data:', error);
            });
    }

    loadLines() {
        return fetch('/data/metadata.json')
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
