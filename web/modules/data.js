import { createGrid } from 'ag-grid-community';

const gridOptions = {
    columnTypes: {
        editableColumn: {
            editable: (p) => {
                return p.node.rowPinned === 'top' && p.node.rowIndex === 0;
            },
            cellClassRules: {
                u: 'x < api.getPinnedTopRow(0).data[colDef.field]',
                o: 'x > api.getPinnedTopRow(0).data[colDef.field]',
                p: 'x == api.getPinnedTopRow(0).data[colDef.field]',
                reset: 'api.getPinnedTopRow(0).data[colDef.field] === undefined || api.getPinnedTopRow(0).data[colDef.field] === null',
            },
            cellStyle: (p) => {
                const line = p.api.getPinnedTopRow(0).data[p.column.colDef.field];

                if (p.node.rowPinned === 'top') {
                    if (p.rowIndex === 0) {
                        return { background: 'rgba(0, 145, 234, 0.1)' };
                    }
                }

                if (line === undefined || line === null) {
                    return {
                        background: 'inherit'
                    };
                }

                if (p.node.rowPinned === 'top') {
                    if (p.rowIndex === 1) {
                        if (p.value > 70) return { background: 'rgba(55, 255, 0, 0.1)' };
                        if (p.value < 30) return { background: 'rgba(255, 0, 0, 0.1)' };
                        return { background: 'inherit' };
                    }
                }
            },
            valueFormatter: (p) => {
                if (p.node.rowPinned === 'top') {
                    if (p.value === undefined || p.value === null || isNaN(p.value)) return '-';

                    if (p.node.rowIndex === 0) {
                        return p.value;
                    }

                    if (p.node.rowIndex === 1) {
                        if (p.value > 70) return ` ↑ ${p.value}%`;
                        if (p.value < 30) return ` ↓ ${100 - p.value}%`;
                        return '-';
                    }

                    return p.value.toFixed(1);
                }
            },
        },
    },
    onCellValueChanged(p) {
        if (p.node.rowPinned === 'top' && p.node.rowIndex === 0) {
            if (p.oldValue === p.newValue) return;

            const rowCount = p.api.getDisplayedRowCount();
            if (rowCount === 0) return;

            const col = p.column.colDef.field;
            p.api.refreshCells({ columns: [col] });

            if (p.newValue === undefined || p.newValue === null) {
                p.api.getPinnedTopRow(1).setDataValue(col, undefined);
                p.api.getPinnedTopRow(2).setDataValue(col, undefined);
                return;
            }

            let hitRateOver = 0;
            let total = 0;

            p.api.forEachNodeAfterFilter((node) => {
                const value = node.data[col];
                if (value >= p.newValue) hitRateOver++;
                total += value;
            });

            p.api.getPinnedTopRow(1).setDataValue(col, Math.round(hitRateOver / rowCount * 100));
            p.api.getPinnedTopRow(2).setDataValue(col, total / rowCount);
        }
    },
    onFilterChanged(p) {
        const rowCount = p.api.getDisplayedRowCount();

        const line = p.api.getPinnedTopRow(0).data;

        const statKeys = Object.entries(line)
            .filter(([k, v]) => k !== 'PLAYER' && v)
            .map(([k, v]) => k);

        const hitRates = {};
        const avgs = {};

        for (const k of statKeys) {
            hitRates[k] = 0;
            avgs[k] = 0;
        }

        p.api.forEachNodeAfterFilter(node => {
            for (const col of statKeys) {
                if (node.data[col] > line[col]) hitRates[col]++;
                avgs[col] += node.data[col];
            }
        });

        for (const k of statKeys) {
            hitRates[k] = Math.round((hitRates[k] / rowCount) * 100);
            avgs[k] = avgs[k] / rowCount;
        }

        p.api.getPinnedTopRow(1).updateData({ ...p.api.getPinnedTopRow(1).data, ...hitRates });
        p.api.getPinnedTopRow(2).updateData({ ...p.api.getPinnedTopRow(2).data, ...avgs });
    }
};

export class Data {
    #gridApi;

    constructor(container) {
        this.getRowData = this.getRowData.bind(this);
        this.container = container;
        this.#gridApi = createGrid(this.container, gridOptions);
        this.rowData = [];
    }

    setTableData(gridOptions) {
        this.#gridApi.setGridOption('columnDefs', gridOptions.columnDefs);

        if (gridOptions.pinnedTopRowData) {
            this.#gridApi.setGridOption('pinnedTopRowData', gridOptions.pinnedTopRowData);
        }

        this.#gridApi.setGridOption('rowData', gridOptions.rowData);
    }

    getRowData() {
        // preallocate array
        const rows = new Array(this.#gridApi.getDisplayedRowCount());

        this.#gridApi.forEachNodeAfterFilter((node, i) => {
            rows[i] = node.data;
        });

        return rows;
    }

    handleNotify(data) {
    }
}
