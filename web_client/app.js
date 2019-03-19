'use strict';

//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

function getGridData() {
    var data = [];
    var x = 0; //starting x and y at 1 so the stroke will show when we make the svg below
    var y = 0;
    //add this to the getGridData function
    var click = 0;

    // iterate for rows
    for (var row = 0; row < 10; row++) {
        data.push( [] );

        // iterate for cells/columns inside rows
        for (var column = 0; column < 10; column++) {
            data[row].push({
                x: x,
                y: y,
                click: click
            });
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

var gridData = getGridData();

var cellLength = 50;

var mapData = [
    {x:0, y: 0, type: 'road', shape: 'curveTopLeft'},
    {x:1, y: 0, type: 'road', shape: 'straightHorizontal'},
    {x:2, y: 0, type: 'road', shape: 'straightHorizontal'},
    {x:3, y: 0, type: 'road', shape: 'tBottom'},
    {x:4, y: 0, type: 'road', shape: 'straightHorizontal'},
    {x:5, y: 0, type: 'road', shape: 'straightHorizontal'},
    {x:6, y: 0, type: 'road', shape: 'curveTopRight'}
];

var svg = d3.select('svg')
.attr('width', '100%')
.attr('height', '100%');


var mapGroup = svg.append('g');
mapGroup
    .selectAll('.mapData')
    .data(mapData)
    .enter()
    .append('svg:image')
    .attr('xlink:href', function(data){
        switch (data.shape) {
            case 'straightHorizontal': return 'images/straightHorizontal.png';
            case 'straightVertical': return 'images/straightVertical.png';
            case 'curveTopLeft': return 'images/curveTopLeft.png';
            case 'curveTopRight': return 'images/curveTopRight.png';
            case 'tBottom': return 'images/tBottom.png';
        }
    })
    .attr('x', function(data) { return data.x * cellLength; })
    .attr('y', function(data) { return data.y * cellLength; })
    .attr('width', function(data) { return cellLength ; })
    .attr('height', function(data) { return cellLength; });

var row = svg.selectAll('.row')
.data(gridData)
.enter().append('g')
.attr('class', 'row');




var column = row.selectAll('.square')
    .data(function(d) { return d; })
    .enter().append('rect')
    .attr('class','square')
    .attr('x', function(d) { return d.x * cellLength; })
    .attr('y', function(d) { return d.y * cellLength; })
    .attr('width', function(d) { return cellLength; })
    .attr('height', function(d) { return cellLength; })
    .style('fill', 'rgba(255, 255, 255, 0)')
    .style('stroke', 'rgba(cellLength, cellLength, cellLength, 5)')
    .on('click', function(d){
        console.log(d);
        d.click ++;
        if ((d.click)%4 === 0 ) { d3.select(this).style('fill','#fff'); }
        if ((d.click)%4 === 1 ) { d3.select(this).style('fill','#2C93E8'); }
        if ((d.click)%4 === 2 ) { d3.select(this).style('fill','#F56C4E'); }
        if ((d.click)%4 === 3 ) { d3.select(this).style('fill','#838690'); }
    });
