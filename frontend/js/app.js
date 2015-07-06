var app = function() {

    // Chart layout functions
    var formatAsYearMonth = d3.time.format("%Y-%m");
    var createTickSeries = function(extent,aggregateBy) {
        // Create an array of dates for axis ticks, by year or month e.g. 2001-01-01, 2002-01-01
        var min = new Date(extent[0]),
            max = new Date(extent[1]),
            ticks = [];

        if (aggregateBy == "year") {
            for (year = min.getUTCFullYear(); year <= max.getUTCFullYear(); year++) {
                ticks.push(new Date(year + "-01-01"));
            }
        }
        return ticks;
    }

    var showYearRegion = function(month) {
            // Given a month (full Date object), get dates 6 months before and after.
            var startMonth = new Date(new Date(month).setMonth(month.getMonth()-6)),
                endMonth = new Date(new Date(month).setMonth(month.getMonth()+6))

            console.log(month + ":" + startMonth + " " + endMonth);
            overviewChart.regions.remove()
            overviewChart.regions.add([
                { axis: "x", start: startMonth, end: endMonth } 
            ]);
        };

    
    // Create overview chart
    var epuPerMonthData = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT (sum(number_of_articles)::real / sum(number_of_newspapers)::real) as epu, to_char(date, 'YYYY-MM') as date FROM epu_tail GROUP BY to_char(date, 'YYYY-MM') ORDER BY to_char(date, 'YYYY-MM')";
    d3.json(epuPerMonthData, function(d) {
        var months = d.rows.map(function(e) { return new Date(e.date); }), // Remove "rows. for final endpoint"
            epu = d.rows.map(function(e) { return e.epu; }); // Remove "rows. for final endpoint"
            formatTooltipTitle = d3.time.format("%Y-%m");

        var overviewChart = c3.generate({
            axis: {
                x: {
                    localtime: false,
                    padding: {
                        left: 0,
                        right: 0
                    },
                    tick: {
                        values: createTickSeries(d3.extent(months),"year"),
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
                colors: {
                    "epu": "black"
                },
                columns: [
                    ["months"].concat(months),
                    ["epu"].concat(epu)
                ],
                // onclick: function (d) { showYearRegion(d.x); },
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
                show: false
            },
            size: {
                height: 100
            },
            tooltip: {
                // show: false
                format: {
                    title: function (d) { return formatAsYearMonth(d); }
                }
            }
        });
    });
}();






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
