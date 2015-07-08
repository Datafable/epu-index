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
        console.log("Tick series: " + extent)
        // Create an array of dates for axis ticks, by year or month e.g. 2001-01-01, 2002-01-01
        var startDate = moment.utc(extent[0]),
            endDate = moment.utc(extent[1]),
            loopingDate = startDate,
            ticks = [];
        if (aggregateBy == "years") {
            loopingDate = startDate.month(0).date(1); // Set month and day to 1 (1st of January)
        } else if (aggregateBy == "months") {
            loopingDate = startDate.date(1); // Set day to 1 (1st of month)
        }
            
        while (loopingDate <= endDate) {
            ticks.push(new Date(loopingDate));
            loopingDate.add(1, aggregateBy);
        }
        return ticks;
    }

    /*
    Chart interaction functions
    */
    var selectYear = function(selectedDate) {
        // Given a selectedDate (e.g. 2010-03-01), get dates 6 months before and after.
        var startDate = moment.utc(selectedDate).subtract(6,"months"),
            endDate = moment.utc(selectedDate).add(6,"months");
        
        console.log(selectedDate + ": " + startDate.format() + " " + endDate.format());

        // Indicate selection on overview chart
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
        var data = "https://epu-index.herokuapp.com/api/epu/?format=json&start=" + startDateString + "&end=" + endDateString;
        d3.json(data, function(d) {
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
    var createOverviewChart = function() {
        // This function creates an overview chart WITH data
        var data = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT (sum(number_of_articles)::real / sum(number_of_newspapers)::real) as epu, to_char(date, 'YYYY-MM') as date FROM epu_tail GROUP BY to_char(date, 'YYYY-MM') ORDER BY to_char(date, 'YYYY-MM')";
        d3.json(data, function(d) {
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
                    onclick: function (d) { selectYear(d.x); },
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
                    left: 20,
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
        });
    };

    var createDetailedChart = function() {
        // This function creates a detailed chart WITHOUT data
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
                left: 20,
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
                    title: function (d) { return formatAsFullDate(d); }
                }
            }
        });
    };

    /*
    Get date range and create charts
    */
    var data = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT max(date), min(date) FROM epu_tail";
    d3.json(data, function(d) {
        console.log(d);
        var lastDate = new Date(d.rows[0].max),
            firstDate = new Date(d.rows[0].min);
            lastDateString = moment.utc(lastDate).format("YYYY-MM-DD"),
            oneYearBeforeLastDateString = moment.utc(lastDate).subtract(1,"years").format("YYYY-MM-DD")

        datesExtent = [firstDate,lastDate];
        createOverviewChart();
        createDetailedChart();
        populateDetailedChart(oneYearBeforeLastDateString,lastDateString);
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
