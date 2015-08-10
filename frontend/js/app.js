var app = (function() {
    "use strict";

    var selectedYearElement = d3.select("#selected-year"),
        selectedDateElement = d3.select("#selected-date"),
        articleElement = d3.select("#article"),
        downloadElement = d3.select("#download"),
        wordCloudElement = d3.select("#word-cloud");
        
    var overviewChart,          // C3 overview chart, showing all data
        detailedChart,          // C3 detailed chart, showing a year of data
        monthsExtent,           // [minimum date, maximum date] of data, rounded to 1st of month
        initialSelectedDate;    // Center date for initial load of detailed chart


    // Chart layout functions
    var formatAsFullDate = d3.time.format("%Y-%m-%d");

    var createTickSeries = function(extent, aggregateBy) {
        // Create an array of dates for x-axis ticks, by year or month
        // E.g. by year: 2012-01-01, 2013-01-01,... or by month: 2012-03-01, 2012-04-01,...
        var firstDate = moment.utc(extent[0]),
            lastDate = moment.utc(extent[1]),
            loopingDate = firstDate,
            ticks = [];

        if (aggregateBy === "years") {
            // Set month and day to 1 (1st of January): 2012-03-21 → 2012-01-01
            loopingDate = firstDate.month(0).date(1);
        } else if (aggregateBy === "months") {
            // Set day to 1 (1st of month): 2012-03-21 → 2012-03-01
            loopingDate = firstDate.date(1);
        }

        while (loopingDate <= lastDate) {
            ticks.push(new Date(loopingDate));
            loopingDate.add(1, aggregateBy);
        }
        return ticks;
    };


    // Chart interaction functions
    var loadYear = function(selectedDate) {
        // Given a selectedDate (e.g. 2010-03-01), get dates 6 months before and after to cover one year and (re)load the detailed chart and download link
        var startDate = moment.utc(selectedDate).subtract(6,"months"), // 2009-09-01
            endDate = moment.utc(selectedDate).add(6,"months").subtract(1,"day"), // 2010-09-01 minus 1 day = 2010-08-31 = cover exactly one year
            epuDataPerDay = "https://epu-index.herokuapp.com/api/epu/?start_date=" + startDate.format("YYYY-MM-DD") + "&end_date=" + endDate.format("YYYY-MM-DD");

        // Update download link
        downloadElement.attr("href", epuDataPerDay + "&format=csv");

        // Update the selected dates in the title
        unloadDate();
        selectedYearElement.text("from " + startDate.format("MMMM YYYY") + " to " + endDate.format("MMMM YYYY"));

        // Show the selected dates on the overview chart
        overviewChart.xgrids([ // regions() would be more appropriate but is buggy and slow
            {value: startDate},
            {value: endDate}
        ]);

        // Reload detailed chart
        d3.json(epuDataPerDay + "&format=json", function(d) {
            var datesPerDay = d.map(function(entry) { return new Date(entry.date); }),
                epuPerDay = d.map(function(entry) { return entry.epu; });
            
            detailedChart.load({
                columns: [
                    ["days"].concat(datesPerDay),
                    ["epu"].concat(epuPerDay)
                ]
            });
        });

        // Reload word cloud
        createWordCloud(startDate, endDate);
    };

    var loadDate = function(selectedDate) {
        // Given a selectedDate (e.g. 2010-03-21), show the highest ranking article and word cloud for that day
        var date = moment.utc(selectedDate),
            highestRankingArticle = "https://epu-index.herokuapp.com/api/highest-ranking-article/?format=json&date=" + date.format("YYYY-MM-DD");

        // Update the selected date in the title
        selectedDateElement.text("on " + date.format("dddd, MMMM Do YYYY"));

        // Show the selected date on the detailed chart
        detailedChart.xgrids([{value: selectedDate}]);

        d3.json(highestRankingArticle, function(d) {
            var html = "";
            if (d.article_title) { // Article returned
                if (d.article_url) {
                    html = d.article_title + ' - <a href="' + d.article_url + '" target="_blank">' + d.article_newspaper + '</a>';
                } else {
                    html = d.article_title + ' - ' + d.article_newspaper;
                }
            } else {
                html = "No article available.";
            }
            articleElement.html(html);
        });

        // Reload word cloud
        createWordCloud(date, date);
    };

    var unloadDate = function() {
        // Remove date from title
        selectedDateElement.text("");
        // Reset article
        articleElement.text("Select a day from the top chart to see the highest ranking article.");
        // Remove vertical line indicating selected date from detailed chart
        detailedChart.xgrids.remove();
    };


    // Chart creation functions
    var createOverviewChart = function(data) {
        // Create an overview chart WITH data, then loadYear()
        var datesPerMonth = data.map(function(entry) { return new Date(entry.month); }),
            epuPerMonth = data.map(function(entry) { return entry.epu; });

        overviewChart = c3.generate({
            axis: {
                x: {
                    localtime: false,
                    padding: {
                        left: 0,
                        right: 0
                    },
                    tick: {
                        values: createTickSeries(monthsExtent, "years"),
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
        loadYear(initialSelectedDate);
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
                        values: createTickSeries(monthsExtent, "months"),
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
                onclick: function(d) { loadDate(d.x); },
                selection: {
                    grouped: true
                },
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

    var createWordCloud = function(startDate, endDate) {
        // Remove previous word cloud
        wordCloudElement.html("");

        // Create new word cloud
        // d3.json("https://epu-index.herokuapp.com/api/.../?format=json&start_date=" + startDate.format("YYYY-MM-DD") + "&end_date=" + endDate.format("YYYY-MM-DD"), function(d) {
        d3.json("http://bartaelterman.cartodb.com/api/v2/sql?q=SELECT text, count FROM term_frequencies limit 60", function(d) {
            var wordsAndCounts = d.rows.map(function(entry) {
                    return  { 
                        inputText: entry.text,
                        inputCount: entry.count
                    };
                }),
                width = parseInt(wordCloudElement.style("width"),10), // Width of parent div
                height = parseInt(wordCloudElement.style("height"),10), // Height of parent div
                minFontSize = 10,
                maxFontSize = 60,
                fontSize = d3.scale.linear() // Function to translate word count to font-size
                    .domain([
                        d3.min(wordsAndCounts, function(d) {
                            return d.inputCount;
                        }),
                        d3.max(wordsAndCounts, function(d) {
                            return d.inputCount;
                        })
                    ])
                    .range([minFontSize,maxFontSize]),
                fontFamily = "Arial, Helvetica, sans-serif",
                textColor = wordCloudElement.style("color"), // Text color of parent div
                angles = [-90, -45, 0]; // Angles at which words can appear

            var draw = function(wordCloudData) {
                wordCloudElement.append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .append("g")
                    .attr("transform", "translate(" + [width / 2, height / 2] + ")") // Centre point
                    .selectAll("text")
                    .data(wordCloudData)
                    .enter().append("text")
                    .style("font-family", d.font)
                    .style("font-size", function(d) { return d.size + "px"; })
                    .attr("text-anchor", "middle")
                    .attr("transform", function(d) {
                        return "translate(" + [d.x, d.y] + ") rotate(" + d.rotate + ")";
                    })
                    .text(function(d) { return d.text; })
                    .style("fill",textColor);
            };

            d3.layout.cloud()
                .size([width, height])
                .words(wordsAndCounts)
                .text(function(d) { return d.inputText.toUpperCase(); }) // Uniformize to uppercase
                .rotate(function() { return angles[Math.floor(Math.random() * angles.length)]; }) // Select one of the angles at random
                .font(fontFamily) // Define here for better display positioning calculation
                .fontSize(function(d) { return fontSize(d.inputCount); }) // Translate count to font-size
                .padding(function(d) { return fontSize(d.inputCount) / 10; }) // Set padding to font-size / 10
                .on("end", draw) // Call the draw function with the word cloud data
                .start();
        });
    };


    // Get EPU data per month, derive date range and create charts
    d3.json("https://epu-index.herokuapp.com/api/epu-per-month/?format=json", function(d) {
        // Set monthsExtent to be used for ticks, e.g [2001-01-01, 2008-12-01]
        // Even though the 1st of month is hardcoded, all downstream functions can work with other dates as well, e.g. createTickSeries() and loadYear().
        monthsExtent = d3.extent(d, function(entry) { return new Date(entry.month + "-01"); });
        // Add one month to the extent, to cover data after the 1st day of the initial last month ([2001-01-01, 2009-01-01])
        monthsExtent[1] = new Date(moment.utc(monthsExtent[1]).add(1,'months'));
        // Set starting point for detailed chart (as 6 months before last month)
        initialSelectedDate = new Date(moment.utc(monthsExtent[1]).subtract(6,'months'));
        
        // Create charts
        createDetailedChart(); // TODO: Is there a chance this chart is before it is referenced, e.g. via unloadDate()?
        createOverviewChart(d);
    });
})();
