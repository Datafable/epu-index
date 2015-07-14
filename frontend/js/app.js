var app = function() {

    /*
    Main variables
    */    
    var overviewChart,
        detailedChart,
        datesExtent;
    
    /*
    Chart layout functions
    */
    var formatAsFullDate = d3.time.format("%Y-%m-%d");

    var createTickSeries = function(extent, aggregateBy) {
        // Create an array of dates for x-axis ticks, by year or month.
        // E.g. by year: 2012-01-01, 2013-01-01,... or by month: 2012-03-01, 2012-04-01,...
        // Start of tick series = year or month of firstDate
        // End of tick series = year or month of one month after lastDate (to have a tick after lastDate)

        var firstDate = moment.utc(extent[0]), // 2012-03-21 stays 2012-03-21
            lastDate = moment.utc(extent[1]).add(1,'months'), // 2013-03-21 → 2013-04-21.
            loopingDate = firstDate,
            ticks = [];

        if (aggregateBy == "years") {
            loopingDate = firstDate.month(0).date(1); // Set month and day to 1 (1st of January): 2012-03-01 → 2012-01-01
        } else if (aggregateBy == "months") {
            loopingDate = firstDate.date(1); // Set day to 1 (1st of month): 2012-03-21 → 2012-03-01
        }
            
        while (loopingDate <= lastDate) {
            ticks.push(new Date(loopingDate));
            loopingDate.add(1, aggregateBy);
        }
        return ticks;
    }

    /*
    Chart interaction functions
    */
    var loadYear = function(selectedDate) {
        // Given a selectedDate (e.g. 2010-03-01), get dates 6 months before and after.
        var startDate = moment.utc(selectedDate).subtract(6,"months"),
            endDate = moment.utc(selectedDate).add(6,"months");

        // Indicate the selected dates on the overview chart
        overviewChart.xgrids([ // regions() would be more appropriate but is buggy and slow
            { value: startDate },
            { value: endDate }
        ]);

        // Reload detailed chart
        populateDetailedChart(startDate.format("YYYY-MM-DD"),endDate.format("YYYY-MM-DD"));
    };

    /*
    Chart data load functions
    */
    var populateDetailedChart = function(startDateString,endDateString) {
        // Retrieve epu data per day and populate chart.
        var epuDataPerDay = "https://epu-index.herokuapp.com/api/epu/?format=json&start=" + startDateString + "&end=" + endDateString;
        d3.json(epuDataPerDay, function(d) {
            var datesPerDay = d.map(function(e) { return new Date(e.date); }),
                epuPerDay = d.map(function(e) { return e.epu; });
            
            detailedChart.load({
                columns: [
                    ["days"].concat(datesPerDay),
                    ["epu"].concat(epuPerDay)
                ]
            });
        });
    };

    /*
    Chart creation functions
    */
    var createOverviewChart = function(lastDateMinusSixMonths) {
        // Create an overview chart WITH data, then loadYear()
        var epuDataPerMonth = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT (sum(number_of_articles)::real / sum(number_of_newspapers)::real) as epu, to_char(date, 'YYYY-MM') as date FROM epu_tail GROUP BY to_char(date, 'YYYY-MM') ORDER BY to_char(date, 'YYYY-MM')";
        d3.json(epuDataPerMonth, function(d) {
            // TODO: update endpoint and remove "rows" from mapping
            var datesPerMonth = d.rows.map(function(e) { return new Date(e.date); }),
                epuPerMonth = d.rows.map(function(e) { return e.epu; });

            overviewChart = c3.generate({
                axis: {
                    x: {
                        localtime: false,
                        padding: {
                            left: 0,
                            right: 0
                        },
                        tick: {
                            values: createTickSeries(datesExtent,"years"),
                            format: "%Y"
                        },
                        type: "timeseries"
                    },
                    y: {
                        show: false
                    }
                },
                bindto: "#overview-chart",
                data: {
                    columns: [
                        ["months"].concat(datesPerMonth),
                        ["epu"].concat(epuPerMonth)
                    ],
                    onclick: function(d) { loadYear(d.x); },
                    selection: {
                        grouped: true // Necessary to have onclick functionality for whole x, not only point
                    },
                    type: "area-spline",
                    x: "months"
                },
                legend: {
                    show: false
                },
                padding: {
                    left: 30,
                    right: 20
                },
                point: {
                    focus: {
                        expand: {
                            r: 4
                        }
                    },
                    r: 0
                },
                tooltip: {
                    show: false
                }
            });
            
            // Once chart is created, load year data. Probably better via oninit(), but overviewChart still undefined at that point.
            loadYear(lastDateMinusSixMonths);
        });
    };

    var createDetailedChart = function() {
        // Creates a detailed chart WITHOUT data
        detailedChart = c3.generate({
            axis: {
                x: {
                    localtime: false,
                    padding: {
                        left: 0,
                        right: 0
                    },
                    tick: {
                        values: createTickSeries(datesExtent,"months"),
                        // This will load ticks for the full potential range,
                        // but only those of the selected data will be shown.
                        format: "%Y-%m"
                    },
                    type: "timeseries"
                }
            },
            bindto: "#detailed-chart",
            data: {
                columns: [
                    ["days"],
                    ["epu"]
                ],
                type: "area-spline",
                x: "days"
            },
            legend: {
                show: false
            },
            padding: {
                left: 30,
                right: 20
            },
            point: {
                focus: {
                    expand: {
                        r: 4
                    }
                },
                r: 0
            },
            tooltip: {
                format: {
                    title: function(d) { return formatAsFullDate(d); },
                    value: function(value) { return value.toFixed(2); }
                }
            }
        });
    };

    /*
    Get date range and create charts
    */
    var extentData = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT max(date), min(date) FROM epu_tail";
    d3.json(extentData, function(d) {
        var firstDate = new Date(d.rows[0].min),
            lastDate = new Date(d.rows[0].max),
            lastDateMinusSixMonths = new Date(moment.utc(lastDate).subtract(6,'months'));

        datesExtent = [firstDate,lastDate];
        createOverviewChart(lastDateMinusSixMonths);
        createDetailedChart();
    });
    
}();



/*

var words = d3.json("http://bartaelterman.cartodb.com/api/v2/sql?q=select text,count from term_frequencies limit 30", function(d) {
    var fill = d3.scale.category20(); // TODO: create custom color schema
    var scalingFactor = 7; // TODO: should be determined based on input counts

    var w = d.rows.map(function(f) {
        return {text: f.text, size: 10 + f.count * scalingFactor};
    });
    d3.layout.cloud().size([300, 300])
        .words(w)
        .padding(0)
        .rotate(function() { return ~~(Math.random() * 2) * 90; })
        .font("Georgia")
        .fontSize(function(d) { return d.size; })
        .on("end", draw)
        .start();

    function draw(words) {
        d3.select("#word-cloud").append("svg")
            .attr("width", 300)
            .attr("height", 300)
            .append("g")
            .attr("transform", "translate(150,150)")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", function(d) { return d.size + "px"; })
            .style("font-family", "Georgia")
            .style("fill", function(d, i) { return fill(i); })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) { return d.text; });
    }
});
*/
