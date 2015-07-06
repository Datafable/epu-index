var app = function() {
    var createAndPopulateOverviewChart = function() {
        // var endpoint = "https://epu-index.herokuapp.com/api/epu/?format=json&start=2013-01-01&end=2013-02-01",
        var endpoint = "http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT (sum(number_of_articles)::real / sum(number_of_newspapers)::real) as epu, to_char(date, 'YYYY-MM') as date FROM epu_tail GROUP BY  to_char(date, 'YYYY-MM') ORDER BY to_char(date, 'YYYY-MM')",
        d3.json(endpoint, function(d) {
            var months = d.rows.map(function(e) { return new Date(e.date); }), // Remove "rows. for final endpoint"
                epu = d.rows.map(function(e) { return e.epu; }), // Remove "rows. for final endpoint"
                overviewChart = c3.generate({
                    axis: {
                        x: {
                            localtime: false,
                            tick: {
                                format: "%Y-%m"
                            },
                            type: "timeseries"
                        },
                        y: {
                            tick: {
                                format: d3.format("O")
                            }
                        }
                    },
                    bindto: "#overview-chart",
                    data: {
                        columns: [
                            ["months"].concat(months),
                            ["epu"].concat(epu)
                        ],
                        type: "spline",
                        x: "months"
                    },
                    legend: {
                        show: false
                    },
                    point: {
                        show: false
                    },
                    size: {
                        height: 100
                    },
                    tooltip: {
                        show: false
                    }
                });
        });
    };
    createAndPopulateOverviewChart();
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

//var epu_index = d3.json("http://epu-index.herokuapp.com/api/epu/", function(d) {
var epu_index = d3.json("http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT (sum(number_of_articles)::real / sum(number_of_newspapers)::real) as epu, to_char(date, 'YYYY-MM') as date FROM epu_tail GROUP BY  to_char(date, 'YYYY-MM') ORDER BY to_char(date, 'YYYY-MM')", function(d) {
    var dates = d.rows.map(function(f) {return new Date(f.date);});
    var values = d.rows.map(function(f) {return f.epu;});
    var dates2 = []
    c3.generate({
        bindto: "#main-line-chart",
        data: {
            x: "date",
            type: "area-spline",
            columns: [
                ["date"].concat(dates),
                ["epu index"].concat(values)
            ]
        },
        axis: {
            x: {
                type: "timeseries",
                tick: {
                    format: "%Y-%m"
                }
            }
        },
        subchart: {
            show: true
        }
    });
});
