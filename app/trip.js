'use strict';

var svg = d3.select('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .style('background-color', '#fff');

var robotsGroup;
var tripsWaitingGroup;
var tripsStartedGroup;

var cellLengthPixels;
var cellLengthMillimeters;
var refreshRateMilliseconds;

var startImages;
var destinationImages;
var mapColumnsCount;
var clicks = 0;

var mapCells;

var gridData;

var trip = {
    status: undefined, // or requested, waiting, started, finished
    start: undefined,
    end: undefined,
    robot_type: undefined
};

d3.json('/map').then(function (mapData){
    cellLengthPixels = mapData['cellLengthPixels'];
    cellLengthMillimeters = mapData['cellLengthMillimeters'];
    refreshRateMilliseconds = mapData['refreshRateMilliseconds'];
    mapColumnsCount = mapData['mapColumnsCount'];
    mapCells = mapData.cells;
    displayMap(mapCells);
    displayGrid();
    robotsGroup = svg.append('g');
    tripsWaitingGroup = svg.append('g');
    tripsStartedGroup = svg.append('g');
    d3.interval(function () {
        d3.json('/robot_status').then(function(robotsData){
            var values = Object.values(robotsData);
            displayRobots(values);
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
        .attr('class', 'mapGroup')
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

    var startGroup = svg.append('g');
    startGroup
        .selectAll('.startGroup')
        .data(mapData)
        .enter()
        .append('svg:image')
        .attr('class', 'startGroup')
        .attr('xlink:href', 'images/startingPoint.png')
        .attr('x', function(data) { return data['column'] * cellLengthPixels  +cellLengthPixels / 4; })
        .attr('y', function(data) { return data['row'] * cellLengthPixels + cellLengthPixels / 4; })
        .attr('width', function() { return cellLengthPixels / 2; })
        .attr('height', function() { return cellLengthPixels / 2; })
        .attr('style', 'visibility: hidden');

    startImages = startGroup.selectAll('.startGroup')._groups[0];


    var destinationGroup = svg.append('g');
    destinationGroup
        .selectAll('.destinationGroup')
        .data(mapData)
        .enter()
        .append('svg:image')
        .attr('class', 'destinationGroup')
        .attr('xlink:href', 'images/destination.png')
        .attr('x', function(data) { return data['column'] * cellLengthPixels  +cellLengthPixels / 4; })
        .attr('y', function(data) { return data['row'] * cellLengthPixels + cellLengthPixels / 4; })
        .attr('width', function() { return cellLengthPixels / 2; })
        .attr('height', function() { return cellLengthPixels / 2; })
        .attr('style', 'visibility: hidden');

    destinationImages = destinationGroup.selectAll('.destinationGroup')._groups[0];
}

function resetTrip(row) {

    trip.start = undefined;
    trip.end = undefined;

    d3.selectAll(startImages).style('visibility', 'hidden');
    d3.selectAll(destinationImages).style('visibility', 'hidden');
    gridData.forEach(function (row) {
        row.forEach(function (column) {
            column.isStartingPoint = false;
            column.isDestination = false;
        });
    });

    row.selectAll('.square')
        .style('fill', 'rgba(255, 255, 255, 0)');

    var buttons = d3.selectAll('.buttonEnabled');
    // if buttons are enabled
    if(buttons._groups[0].length > 0){
        buttons.attr('class', 'buttonDisabled');
    }
}

function displayGrid() {
//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

    function getGridData() {
        var data = [];
        var x = 0;
        var y = 0;

        // iterate for rows
        for (var row = 0; row < 7; row++) {
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
        .on('click', function (data) {
            var index = data.y * mapColumnsCount + data.x;
            console.log(data);
            if(mapCells[index].type==="building"){
                return;
            }
            clicks = (clicks + 1) % 3;
            if(clicks === 0){
                resetTrip(row);
            }


            // starting point
            if (clicks === 1 && ! data.isDestination){
                // d3.select(this).style('fill', '#fff');
                data.isStartingPoint = true;
                var element = startImages[index];
                d3.select(element).style('visibility', 'visible');
                trip.start = {row : data.y, column: data.x}
            }
            if (clicks === 1 && data.isDestination){
                clicks = clicks - 1;
            }
            // destination
            if (clicks === 2 && ! data.isStartingPoint){
                trip.end = {row : data.y, column: data.x}
                // d3.select(this).style('fill', '#f00');
                data.isDestination = true;
                var element = destinationImages[index];
                d3.select(element).style('visibility', 'visible');

                var buttons = d3.selectAll('.buttonDisabled');
                // if buttons are enabled
                if(buttons._groups[0].length > 0){
                    buttons.attr('class', 'buttonEnabled');
                }
            }
            if (clicks === 2 && data.isStartingPoint){
                clicks = clicks - 1;
            }

            console.log(trip);
        });
}

function transformRobot(data) {
    var xTranslate = millimetersToPixels(data.y + 95.25) + cellLengthPixels - cellLengthPixels / 6;
    var yTranslate = millimetersToPixels(data.x) + 2 * cellLengthPixels - cellLengthPixels / 3;
    var rotate = 'rotate(' + (- data.rotation) + ',' + cellLengthPixels/3.0 + ',' + cellLengthPixels/3.0+ ')';
    return 'translate(' + xTranslate + ',' + yTranslate + ') ' + rotate;
}

function displayRobots(robotsData){
    var robots = robotsGroup
            .selectAll('image')
            .data(robotsData);
    robots.transition().duration(refreshRateMilliseconds)
        .ease(d3.easeLinear)
        .attr('transform', transformRobot);
    robots.enter()
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
    robots.exit().remove();

    var tripsWaitingData = [];
    robotsData.forEach(function (data) {
        if (data['trip'] != null && data['trip'].status === 'waiting') {
            tripsWaitingData.push(data);
        }
    });

    var tripsWaiting = tripsWaitingGroup
        .selectAll('image')
        .data(tripsWaitingData);
    tripsWaiting.transition().duration(refreshRateMilliseconds)
        .ease(d3.easeLinear)
        .attr('transform', transformRobot);
    tripsWaiting.enter()
        .append('svg:image')
        .attr('transform', transformRobot)
        .attr('class', 'robot')
        .attr('xlink:href', 'images/waiting.svg')
        .attr('width', function () {
            return cellLengthPixels / 3.0;
        })
        .attr('height', function () {
            return cellLengthPixels / 3.0;
        });
    tripsWaiting.exit().remove();

    var tripsStartedData = [];
    robotsData.forEach(function (data) {
        if (data['trip'] != null && data['trip'].status === 'started') {
            tripsStartedData.push(data);
        }
    });

    var tripsStarted = tripsStartedGroup
        .selectAll('image')
        .data(tripsStartedData);
    tripsStarted.transition().duration(refreshRateMilliseconds)
        .ease(d3.easeLinear)
        .attr('transform', transformRobot);
    tripsStarted.enter()
        .append('svg:image')
        .attr('transform', transformRobot)
        .attr('class', 'robot')
        .attr('xlink:href', 'images/started.svg')
        .attr('width', function () {
            return cellLengthPixels / 3.0;
        })
        .attr('height', function () {
            return cellLengthPixels / 3.0;
        });
    tripsStarted.exit().remove();
}


function buttonClicked(robotType){
    var buttons = d3.selectAll('.buttonEnabled');
    // if buttons are enabled
    if(buttons._groups[0].length > 0){
        trip.robot_type = robotType;
        trip.status = 'requested';
        buttons.attr('class', 'buttonDisabled');
        d3.json('/trip', {
            method:"POST",
            body: JSON.stringify(trip),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        })
            .then(function (value) {
                console.log(value)
            }).catch(function (reason) {
                console.log(reason);
                d3.select('#notification')
                    .style('visibility', 'visible')
                    .text('The trip request can not be fulfilled. Please try again later.');
                buttons.attr('class', 'buttonEnabled');
                setTimeout(function () {
                    d3.select('#notification')
                        .style('visibility', 'hidden')
            }, 2000);
        });
    }
}