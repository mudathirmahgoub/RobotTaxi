'use strict';

//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

var svg = d3.select('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .style('background-color', '#fff');
    // .call(d3.zoom().on("zoom", function () {
    //     svg.attr("transform", d3.event.transform)
    // }));

var cellLengthPixels;
var cellLengthMillimeters;
var refreshRateMilliseconds;

var clicks = 0;

var gridData;

d3.json('/map').then(function (mapData){
    cellLengthPixels = mapData['cellLengthPixels'];
    cellLengthMillimeters = mapData['cellLengthMillimeters'];
    refreshRateMilliseconds = mapData['refreshRateMilliseconds'];
    displayMap(mapData.cells);
    displayGrid();
    var robotsGroup = svg.append('g');
    d3.interval(function () {
        d3.json('/robot_status').then(function(robotsData){
            var values = Object.values(robotsData);
            displayRobots(values, robotsGroup);
        });
    }, refreshRateMilliseconds);
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
        .attr('x', function(data) { return data['column'] * cellLengthPixels; })
        .attr('y', function(data) { return data['row'] * cellLengthPixels; })
        .attr('width', function() { return cellLengthPixels ; })
        .attr('height', function() { return cellLengthPixels; });
}

function displayGrid() {

    function getGridData() {
        var data = [];
        var x = 0;
        var y = 0;

        // iterate for rows
        for (var row = 0; row < 9; row++) {
            data.push([]);

            // iterate for cells/columns inside rows
            for (var column = 0; column < 9; column++) {
                data[row].push({
                    x: x,
                    y: y,
                    isStartingPoint: false,
                    isDestination: false
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

    gridData = getGridData();

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

            clicks = (clicks + 1) % 3;


            if(clicks === 0){
                gridData.forEach(function (data) {
                    data.isStartingPoint = false;
                    data.isDestination = false;
                } );

                row.selectAll('.square')
                    .style('fill', 'rgba(255, 255, 255, 0)');
            }

            if(clicks === 1){
                d.isStartingPoint = true;
            }
            if(clicks === 2){
                d.isDestination = true;
            }
            // starting point
            if (d.isStartingPoint && ! d.isDestination){
                d3.select(this).style('fill', '#fff');
            }
            // destination
            if (d.isDestination && ! d.isStartingPoint){
                d3.select(this).style('fill', '#f00');
            }
        });
}

function transformRobot(data) {
    var xTranslate = millimetersToPixels(data.y + 95.25) + cellLengthPixels - cellLengthPixels / 6;
    var yTranslate = millimetersToPixels(data.x) + 2 * cellLengthPixels - cellLengthPixels / 3;
    var rotate = 'rotate(' + (- data.rotation) + ',' + cellLengthPixels/3.0 + ',' + cellLengthPixels/3.0+ ')';
    return 'translate(' + xTranslate + ',' + yTranslate + ') ' + rotate;
}

function displayRobots(robotsData, robotsGroup){
    var group = robotsGroup
            .selectAll('image')
            .data(robotsData);
    group.transition().duration(refreshRateMilliseconds)
        .ease(d3.easeLinear)
        .attr('transform', transformRobot);
    group.enter()
        .append('svg:image')
        .attr('transform', transformRobot)
        .attr('class', 'robot')
        .attr('xlink:href', 'images/cozmo.png')
        .attr('width', function() { return cellLengthPixels / 3.0 ; })
        .attr('height', function() { return cellLengthPixels / 3.0 ; });
    group.exit().remove();
}