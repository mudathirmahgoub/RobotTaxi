'use strict';

//based on http://www.cagrimmett.com/til/2016/08/17/d3-lets-make-a-grid.html

var svg = d3.select('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .style('background-color', '#707477');

var cellLength = 50;

d3.json('/map').then(function (mapData){
    displayMap(mapData);
    displayGrid();
    var robotsGroup = svg.append('g');
    updateRobotsStatus();
    function updateRobotsStatus() {
        d3.json('/robot_status').then(function(robotsData){
            var values = Object.values(robotsData);
            for (var i = 0; i < values.length ; i++) {
                delete values[i]['update_time'];
            }
            console.log(values);
            displayRobots(values, robotsGroup);
        });
        setTimeout(function () {
            updateRobotsStatus();
        }, 1000);
    }
});



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
                return 'images/' + data.shape + '.png';
            }
        })
        .attr('x', function(data) { return data.x * cellLength; })
        .attr('y', function(data) { return data.y * cellLength; })
        .attr('width', function(data) { return cellLength ; })
        .attr('height', function(data) { return cellLength; });
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

    var column = row.selectAll('.square')
        .data(function (d) {
            return d;
        })
        .enter().append('rect')
        .attr('class', 'square')
        .attr('x', function (d) {
            return d.x * cellLength;
        })
        .attr('y', function (d) {
            return d.y * cellLength;
        })
        .attr('width', function (d) {
            return cellLength;
        })
        .attr('height', function (d) {
            return cellLength;
        })
        .style('fill', 'rgba(255, 255, 255, 0)')
        .style('stroke', 'rgba(cellLength, cellLength, cellLength, 5)')
        .on('click', function (d) {
            console.log(d);
            d.click++;
            if ((d.click) % 4 === 0) {
                d3.select(this).style('fill', '#fff');
            }
            if ((d.click) % 4 === 1) {
                d3.select(this).style('fill', '#2C93E8');
            }
            if ((d.click) % 4 === 2) {
                d3.select(this).style('fill', '#F56C4E');
            }
            if ((d.click) % 4 === 3) {
                d3.select(this).style('fill', '#838690');
            }
        });
}

function displayRobots(robotsData, robotsGroup){
    var group = robotsGroup
            .selectAll('image')
            .data(robotsData);
    group.transition().duration(1000)
        .attr('x', function(data) { return data.x; })
        .attr('y', function(data) { return data.y; })
    group.enter()
        .append('svg:image')
        .attr('x', function(data) { console.log(data); return data.x; })
        .attr('y', function(data) { return data.y; })
        .attr('class', 'robot')
        .attr('xlink:href', function(data){
           return "images/cozmoUp.png";
        })
        .attr('width', function(data) { return cellLength / 3 ; })
        .attr('height', function(data) { return cellLength / 3; });
    group.exit().remove();
}

// // dynamic data
//
// var robotsData = [
//     {"robot_id": 1, "x": 125, "y": 120, "angle_z_degrees": 0, "update_time": ""},
//     {"robot_id": 2, "x": 225, "y": 120, "angle_z_degrees": 0, "update_time": ""},
//     {"robot_id": 3, "x": 325, "y": 220, "angle_z_degrees": 0, "update_time": ""},
//     {"robot_id": 4, "x": 425, "y": 220, "angle_z_degrees": 0, "update_time": ""}
// ];