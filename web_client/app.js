'use strict';

//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

function gridData() {
    var data = new Array();
    var x = 0; //starting x and y at 1 so the stroke will show when we make the grid below
    var y = 0;
    //add this to the gridData function
    var click = 0;

    // iterate for rows
    for (var row = 0; row < 10; row++) {
        data.push( new Array() );

        // iterate for cells/columns inside rows
        for (var column = 0; column < 10; column++) {
            data[row].push({
                x: x,
                y: y,
                width: 50,
                height: 50,
                click: click
            })
            // increment the x position
            x += 1;
        }
        // reset the x position after a row is complete
        x = 0;
        // increment the y position for the next row
        y += 1;
    }
    return data;
}

var gridData = gridData();

var grid = d3.select('#grid')
.append('svg')
.attr('width', '100%')
.attr('height', '100%');


var row = grid.selectAll(".row")
.data(gridData)
.enter().append('g')
.attr('class', 'row');


var map = row.selectAll(".square")
    .data(function(d) { return d; })
    .enter()
    .append('svg:image')
    .attr("xlink:href", "images/straight.png")
    .attr("x", function(d) { return d.x * 50; })
    .attr("y", function(d) { return d.y * 50; })
    .attr("width", function(d) { return d.width ; })
    .attr("height", function(d) { return d.height; });

var column = row.selectAll(".square")
    .data(function(d) { return d; })
    .enter().append("rect")
    .attr("class","square")
    .attr("x", function(d) { return d.x * 50; })
    .attr("y", function(d) { return d.y * 50; })
    .attr("width", function(d) { return d.width ; })
    .attr("height", function(d) { return d.height; })
    .style("fill", "rgba(255, 255, 255, 0)")
    .style("stroke", "rgba(50, 50, 50, 5)")
    .on('click', function(d){
        console.log(d);
        d.click ++;
        if ((d.click)%4 == 0 ) { d3.select(this).style("fill","#fff"); }
        if ((d.click)%4 == 1 ) { d3.select(this).style("fill","#2C93E8"); }
        if ((d.click)%4 == 2 ) { d3.select(this).style("fill","#F56C4E"); }
        if ((d.click)%4 == 3 ) { d3.select(this).style("fill","#838690"); }
    });

var grid = d3.select('#grid')
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%');


var row = grid.selectAll(".row")
    .data(map)
    .enter().append('g')
    .attr('class', 'row');

