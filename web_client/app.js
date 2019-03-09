'use strict';

var data = [{ date: "10/25/2018", value: 1 },
{ date: "10/26/2018", value: 3 },
{ date: "10/27/2018", value: 0 },
{ date: "10/28/2018", value: 0 },
{ date: "10/29/2018", value: 5 },
{ date: "10/30/2018", value: 8 },
{ date: "10/31/2018", value: 7 },
{ date: "11/01/2018", value: 11 },
{ date: "11/02/2018", value: 23 },
{ date: "11/03/2018", value: 13 },
{ date: "11/04/2018", value: 15 },
{ date: "11/05/2018", value: 37 }
];

var margin = 50;

var width = 1024;
var height = 768;

var dataGroup = d3.select("body").append("svg")
    .attr("width", width + margin)
    .attr("height", height + 2 * margin)
    .append("g")
    .attr("transform", "translate(" + margin + ", " + margin + ")");

var line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.value))
    ;

var parseTime = d3.timeParse("%m/%d/%Y");

data.forEach(function (d) {
    d.date = parseTime(d.date);
});

var x = d3.scaleTime()
    .domain(d3.extent(data, function (d) { return d.date; }))
    .range([0, width])
    ;

var y = d3.scaleLinear()
    .domain(d3.extent(data, function (d) { return d.value }))
    .range([height, 0])
    ;

dataGroup.append("path")
    .data([data])
    .attr("fill", "none")
    .attr("stroke", "red")
    .attr("d", line)

var xAxisGroup = dataGroup
    .append("g")
    .attr("class", "xAxisGroup")
    .attr("transform", "translate(0," + height + ")")

var xAxis = d3.axisBottom(x)
    .tickFormat(d3.timeFormat("%Y-%m-%d"));

xAxis(xAxisGroup);

var yAxisGroup = dataGroup
    .append("g")
    .attr("class", "yAxisGroup")

var yAxis = d3.axisLeft(y);

yAxis(yAxisGroup);