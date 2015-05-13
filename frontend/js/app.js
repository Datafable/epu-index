var words = d3.json('http://bartaelterman.cartodb.com/api/v2/sql?q=select text,count from term_frequencies limit 30', function(d) {
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
        d3.select("body").append("svg")
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

//var epu_index = d3.json('http://epu-index.herokuapp.com/api/epu/', function(d) {
var epu_index = d3.json("http://bartaelterman.cartodb.com/api/v2/sql?q=select date,epu from epu_tail where date<='2013-12-31' and date>='2013-01-01'", function(d) {
    var dates = d.rows.map(function(f) {return new Date(f.date);});
    var values = d.rows.map(function(f) {return f.epu;});
    c3.generate({
        bindto: "#linechart",
        data: {
            x: "date",
            columns: [
                ["date"].concat(dates),
                ["epu index"].concat(values)
            ]
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    format: "%Y-%m-%d"
                }
            }
        },
        subchart: {
            show: true
        }
    });
})