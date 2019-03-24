'use strict';

//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

var svg = d3.select('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .style('background-color', '#fff');

var cellLengthPixels;
var cellLengthMillimeters;
var refreshRateMilliseconds;

d3.json('/map').then(function (mapData){
    cellLengthPixels = mapData['cellLengthPixels'];
    cellLengthMillimeters = mapData['cellLengthMillimeters'];
    refreshRateMilliseconds = mapData['refreshRateMilliseconds'];
    displayMap(mapData.cells);
    displayGrid();
    var robotsGroup = svg.append('g');
    updateRobotsStatus();
    function updateRobotsStatus() {
        d3.json('/robot_status').then(function(robotsData){
            var values = Object.values(robotsData);
            displayRobots(values, robotsGroup);
        });
        setTimeout(function () {
            updateRobotsStatus();
        }, refreshRateMilliseconds);
    }
});

function millimetersToPixels(x){
    return x / cellLengthMillimeters * cellLengthPixels;
}

function displayMap(mapData){

    var mapGroup = svg.append('g');
    mapGroup
        .selectAll('.mapData')
        .data(mapData)
        .enter()
        .append('svg:image')
        .attr('class', 'building')
        .attr('xlink:href', function(data){
            if(data.type ==='road') {
                switch (data.shape) {
                    case 'straightHorizontal':
                        return 'images/straightHorizontal.png';
                    case 'straightVertical':
                        return 'images/straightVertical.png';
                    case 'curveTopLeft':
                        return 'images/curveTopLeft.png';
                    case 'curveTopRight':
                        return 'images/curveTopRight.png';
                    case 'curveBottomLeft':
                        return 'images/curveBottomLeft.png';
                    case 'curveBottomRight':
                        return 'images/curveBottomRight.png';
                    case 'tTop':
                        return 'images/tTop.png';
                    case 'tRight':
                        return 'images/tRight.png';
                    case 'tBottom':
                        return 'images/tBottom.png';
                    case 'tLeft':
                        return 'images/tLeft.png';
                    case 'cross':
                        return 'images/cross.png';
                }
            }
            if (data.type === 'building'){
                return '';
                // return 'images/' + data.shape + '.png';
            }
        })
        .attr('x', function(data) { return data['row'] * cellLengthPixels; })
        .attr('y', function(data) { return data['column'] * cellLengthPixels; })
        .attr('width', function() { return cellLengthPixels ; })
        .attr('height', function() { return cellLengthPixels; });
}

function displayGrid() {

    function getGridData() {
        var data = [];
        var x = 0; //starting x and y at 1 so the stroke will show when we make the svg below
        var y = 0;
        //add this to the getGridData function
        var click = 0;

        // iterate for rows
        for (var row = 0; row < 9; row++) {
            data.push([]);

            // iterate for cells/columns inside rows
            for (var column = 0; column < 9; column++) {
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

    var row = svg.selectAll('.row')
        .data(gridData)
        .enter().append('g')
        .attr('class', 'row');

    row.selectAll('.square')
        .data(function (d) {
            return d;
        })
        .enter().append('rect')
        .attr('class', 'square')
        .attr('x', function (d) {
            return d.x * cellLengthPixels;
        })
        .attr('y', function (d) {
            return d.y * cellLengthPixels;
        })
        .attr('width', function () {
            return cellLengthPixels;
        })
        .attr('height', function () {
            return cellLengthPixels;
        })
        .style('fill', 'rgba(255, 255, 255, 0)')
        .on('click', function (d) {
            console.log(d);
            d.click++;
            if ((d.click) % 2 === 1)
            {
                d3.select(this).style('fill', '#fff');
            }
            else {
                d3.select(this).style('fill', 'rgba(255, 255, 255, 0)');
            }
        });
}

function displayRobots(robotsData, robotsGroup){
    var group = robotsGroup
            .selectAll('image')
            .data(robotsData);
    group.transition().duration(refreshRateMilliseconds)
        .attr('x', function(data) { return millimetersToPixels(data.x) + cellLengthPixels/5; })
        .attr('y', function(data) { return millimetersToPixels(data.y) + cellLengthPixels/5; })
    group.enter()
        .append('svg:image')
        .attr('x', function(data) { return millimetersToPixels(data.x) + cellLengthPixels/5; })
        .attr('y', function(data) { return millimetersToPixels(data.y) + cellLengthPixels/5; })
        .attr('class', 'robot')
        .attr('xlink:href', function(){
           return "images/cozmo.png";
        })
        .attr('width', function() { return cellLengthPixels / 3 ; })
        .attr('height', function() { return cellLengthPixels / 3; });
    group.exit().remove();
}
