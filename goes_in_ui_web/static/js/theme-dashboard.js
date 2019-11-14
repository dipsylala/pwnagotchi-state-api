var pwnagotchi = pwnagotchi || {};

pwnagotchi.dashboard = (function () {
    let _x = [];
    let _temperature = [];
    let _memory = [];
    let _cpu = [];
    let _pwnd_run = [];
    let _last_graph = null;

    var _defaultGraphSettings = {
        editable: false,
        staticPlot: true,
        displayModeBar: false,
        showLink: false,
        displaylogo: false,
        responsive: true
    };

    let _storeResults = function (results) {
        _temperature.push(results.temperature.toFixed(2))
        _memory.push(results.memory * 100).toFixed(2)
        _cpu.push((results.cpu * 100).toFixed(2))
        _pwnd_run.push(results.pwnd_run);
    };

    let _archiveOldResults = function () {
        if (_x.length > 400) {
            _x.shift();
            _temperature.shift();
            _memory.shift();
            _cpu.shift();
            _pwnd_run.shift();
        }
    };

    let populateDisplayAndGraph = function (results) {
        pwnagotchi.populateDisplay(results);
        let now = new Date();

        if (_last_graph !== null && Math.abs(now - _last_graph) < 10000) {
            return
        }

        _last_graph = now;
        _x.push(now);
        _storeResults(results);
        _archiveOldResults();

        let olderTime = now.setMinutes(now.getMinutes() - 30);
        let futureTime = now.setMinutes(now.getMinutes() + 30);

        Plotly.relayout("time-series-hardware", 'xaxis.range', [olderTime, futureTime])
        Plotly.relayout("time-series-pwned", 'xaxis.range', [olderTime, futureTime])

        Plotly.redraw("time-series-hardware");
        Plotly.redraw("time-series-pwned");
    };

    let initialise = function () {
        let temp_graph = { type: "scatter", mode: "lines", name: 'Temp (c)', x: _x, y: _temperature, line: {color: '#FF0000'}};
        let cpu_graph = {type: "scatter", mode: "lines", name: 'CPU (%)', x: _x, y: _cpu, line: {color: '#00FF00'}};
        let mem_graph = {type: "scatter", mode: "lines", name: 'Mem (%)', x: _x, y: _memory, line: {color: '#0000FF'}};
        let data = [temp_graph, cpu_graph, mem_graph]

        let layout = {
            title: 'Hardware',
            xaxis: {
                type: 'date',
                tickformat: '%H:%M'
            },
            yaxis: {
                autorange: false,
                range: [10, 100],
                type: 'linear'
            },
            font: {
                family: 'Courier New, monospace',
                size: 16,
                color: '#7f7f7f'
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            autosize: false,
              width: 300,
              height: 250,
              margin: {
                l: 50,
                r: 50,
                b: 25,
                t: 50,
                pad: 4
              }
        };
        Plotly.newPlot('time-series-hardware', data, layout, _defaultGraphSettings);

        let pwned_layout = {
            title: 'Pwned',
            xaxis: {
                type: 'date',
                tickformat: '%H:%M'
            },
            yaxis: {
                autorange: true,
                rangemode: 'nonnegative',
                type: 'linear',
                tickformat: ',d'
            },
            font: {
                family: 'Courier New, monospace',
                size: 16,
                color: '#7f7f7f'
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0)',
              autosize: false,
              width: 300,
              height: 250,
              margin: {
                l: 50,
                r: 50,
                b: 25,
                t: 50,
                pad: 4
              }
        };

        let pwnd_data = [
            {
                x: _x,
                y: _pwnd_run,
                type: 'scatter'
            }
        ];

        Plotly.newPlot('time-series-pwned', pwnd_data, pwned_layout, _defaultGraphSettings);
    };

    return {
        initialise: initialise,
        populateDisplayAndGraph: populateDisplayAndGraph
    }
}());