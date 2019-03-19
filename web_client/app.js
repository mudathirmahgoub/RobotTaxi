'use strict';

//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

function gridData() {
    var data = new Array();
    var xPosition = 1; //starting xPosition and yPosition at 1 so the stroke will show when we make the grid below
    var yPosition = 1;
    var width = 50;
    var height = 50;

    //add this to the gridData function
    var click = 0;

    // iterate for rows
    for (var row = 0; row < 10; row++) {
        data.push( new Array() );

        // iterate for cells/columns inside rows
        for (var column = 0; column < 10; column++) {
            data[row].push({
                x: xPosition,
                y: yPosition,
                width: width,
                height: height,
                click: click
            })
            // increment the x position. I.e. move it over by 50 (width variable)
            xPosition += width;
        }
        // reset the x position after a row is complete
        xPosition = 1;
        // increment the y position for the next row. Move it down 50 (height variable)
        yPosition += height;
    }
    return data;
}

var gridData = gridData();

var grid = d3.select('#grid')
.append('svg')
.attr('width', '510px')
.attr('height', '510px');


var row = grid.selectAll(".row")
.data(gridData)
.enter().append('g')
.attr('class', 'row');


var column = row.selectAll(".square")
    .data(function(d) { return d; })
    .enter().append("rect")
    .attr("class","square")
    .attr("x", function(d) { return d.x; })
    .attr("y", function(d) { return d.y; })
    .attr("width", function(d) { return d.width; })
    .attr("height", function(d) { return d.height; })
    .style("fill", "#fff")
    .style("stroke", "#222")
    .on('click', function(d){
        d.click ++;
        if ((d.click)%4 == 0 ) { d3.select(this).style("fill","#fff"); }
        if ((d.click)%4 == 1 ) { d3.select(this).style("fill","#2C93E8"); }
        if ((d.click)%4 == 2 ) { d3.select(this).style("fill","#F56C4E"); }
        if ((d.click)%4 == 3 ) { d3.select(this).style("fill","#838690"); }
    });