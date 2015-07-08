var app = function() {
    /*
    Chart layout functions
    */
    var formatAsFullDate = d3.time.format("%Y-%m-%d");
    var createTickSeries = function(extent,aggregateBy) {
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

        overviewChart.regions.remove();
        overviewChart.regions.add([
            { axis: "x", start: startDate, end: endDate } 
        ]);
    };

    /*
    Create overview chart
    */
    var overviewChart,
        epuPerMonth = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT (sum(number_of_articles)::real / sum(number_of_newspapers)::real) as epu, to_char(date, 'YYYY-MM') as date FROM epu_tail GROUP BY to_char(date, 'YYYY-MM') ORDER BY to_char(date, 'YYYY-MM')";
    d3.json(epuPerMonth, function(d) {
        var months = d.rows.map(function(e) { return new Date(e.date); }), // Remove "rows. for final endpoint"
            epu = d.rows.map(function(e) { return e.epu; }); // Remove "rows. for final endpoint"

        overviewChart = c3.generate({
            axis: {
                x: {
                    localtime: false,
                    padding: {
                        left: 0,
                        right: 0
                    },
                    tick: {
                        values: createTickSeries(d3.extent(months),"years"),
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
                    ["months"].concat(months),
                    ["epu"].concat(epu)
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
            regions: [
                { axis: "x", start: "2011-11-03", end: "2012-11-02", class: "selection"}
            ],
            tooltip: {
                show: false
            }
        });
    });

    /*
    Create detailed chart
    */
    var detailedChart,
        epuPerDay = "https://epu-index.herokuapp.com/api/epu/?format=json&start=2011-11-03&end=2012-11-02";
    d3.json(epuPerDay, function(d) {
        var days = d.map(function(e) { return new Date(e.date); }),
            epu = d.map(function(e) { return e.epu; });

        detailedChart = c3.generate({
            axis: {
                x: {
                    localtime: false,
                    padding: {
                        left: 0,
                        right: 0
                    },
                    tick: {
                        values: createTickSeries(d3.extent(days),"months"),
                        format: "%Y-%m"
                    },
                    type: "timeseries"
                }
            },
            bindto: "#detailed-chart",
            data: {
                columns: [
                    ["days"].concat(days),
                    ["epu"].concat(epu)
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
