'use strict';

var svg = d3.select('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .style('background-color', '#fff');

var cellLengthPixels;
var cellLengthMillimeters;
var refreshRateMilliseconds;

// get the map data from the server
d3.json('/map').then(function (mapData){
    // read the global variables
    cellLengthPixels = mapData['cellLengthPixels'];
    cellLengthMillimeters = mapData['cellLengthMillimeters'];
    refreshRateMilliseconds = mapData['refreshRateMilliseconds'];
    displayMap(mapData.cells);

    var robotsGroup = svg.append('g');

    // get the status of all robots periodically from the server
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
            }
        })
        .attr('x', function(data) { return data['column'] * cellLengthPixels; })
        .attr('y', function(data) { return data['row'] * cellLengthPixels; })
        .attr('width', function() { return cellLengthPixels ; })
        .attr('height', function() { return cellLengthPixels; });
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
        .attr('xlink:href', function(data){
            switch(data['robot_type']){
                case 'cozmo':
                    return 'images/cozmo.png';
                case 'vector':
                    return 'images/vector.png';
            }
        })
        .attr('width', function() { return cellLengthPixels / 3.0 ; })
        .attr('height', function() { return cellLengthPixels / 3.0 ; });
    group.exit().remove();
}
