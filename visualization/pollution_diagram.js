// load data
data_path = '../data/states_pollution_dense.json'

d3.json(data_path).then(function(data) {

    // console.log(data)
    
    margin = {'top': 50, 'bottom': 50, 'left': 50, 'right': 50}

    // Based off this: https://observablehq.com/@d3/directed-chord-diagram/2
    // chord chart dimensions
    const width = 500 + margin.left + margin.right
    const height = width + margin.top + margin.bottom
    const innerRadius = Math.min(width, height) * 0.5 - margin.top
    const outerRadius = innerRadius + 10

    // just just the data for california for now
    var state_data = data.find(d => d.state == 'USA')

    matrix = state_data.data.data // yikes. my naming conventions suck
    naics = state_data.data.index
    pollutants = state_data.data.columns

    const chord = d3.chordDirected()
        .padAngle(12 / innerRadius)
        //.sortSubgroups(d3.descending)
        //.sortChords(d3.descending);

    const chords = chord(matrix);

    const arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    const ribbon = d3.ribbonArrow()
        .radius(innerRadius - 0.5)
        .padAngle(1 / innerRadius);

    const colors = ['#09152F','#1D0E58','#621282','#AE138A','#DD1346','#F25D2C,', '#F8D254','#D8FC7D','#BAFFA8','#D6FFE3']//d3.schemeCategory10;

    // create chart elements
    var svg = d3.select("#chordChart")
    .append("svg")
        .attr("width", width)
        .attr("height", height)
    .append("g")
        .attr("transform", `translate(${width/2},${height/2})`)
    
    // add plot title
    svg.append('text')
    //.attr("transform", `translate(${0},${-height/2 + margin.top})`)
    .attr('y', -height/2 + margin.top + 20)
    .attr('text-anchor', 'middle')
    .text(`Top Polluting Industries and Pollutants in ${state_data.state}`)


    // add the groups on the outer part of the circle
    var group = svg
        .append("g")
        .selectAll("g")
        .data(chords.groups)

    // group labeling method taken from here: https://stackoverflow.com/questions/43259039/how-to-add-labels-into-the-arc-of-a-chord-diagram-in-d3-js
    // make outer arcs
    group
    .enter()
    .append("g")
    .append("path")
    .style("fill", function(d, i) {
        // only  color in nodes for industries
        return i < naics.length / 2 ? colors[d.index] : 'grey'
    })
    .style("stroke", "black")
    .attr("id", function(d, i) { return "group" + d.index; })
    .attr("d", arc)

    /*
    // This code generates text around each cercle segment to show the node names. It doesn't put text in the right place, likely because of the chart coordinate system.
    group
    .enter()
    .append("text")
    .each(function(d) { d.angle = (d.startAngle + d.endAngle) / 2; })
    .attr("dy", '.35em')
    .attr("class", "titles")
    .attr("transform", function(d) {
        return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
            + "translate(" + (innerRadius + 26) + ")"
            + (d.angle > Math.PI ? "rotate(180)" : "");
      })
      .style("text-anchor", function(d) { return d.angle > Math.PI ? "end" : null; })
    .append("textPath")
    .attr("xlink:href", function(d) { return "#group" + d.index; })
    //.attr("startOffset", '50%')
    .text(function(d) { 
        console.log(naics[d.index])
        return naics[d.index]
        })
    .style("fill", "black")
    .style('font-size', 6)
    */

    // Add a tooltip div. Here I define the general feature of the tooltip: stuff that do not depend on the data point.
    // Its opacity is set to 0: we don't see it by default.
    var tooltip = d3.select("#chordChart")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip")
    .style("background-color", "white")
    .style("border", "solid")
    .style("border-width", "1px")
    .style("border-radius", "5px")
    .style("padding", "10px")

}).catch(error => console.log(error))

function createChordChart(svg, emissionsData, state) {
    let d_select = emissionsData.find(d => d === state)

    matrix = d_select.data.data // yikes. my naming conventions suck
    naics = d_select.data.index
    pollutants = d_select.data.columns

    let chord = d3.chordDirected()
        .padAngle(12 / innerRadius)

    let chords = chord(matrix);

    let arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    let ribbon = d3.ribbonArrow()
        .radius(innerRadius - 0.5)
        .padAngle(1 / innerRadius);

    let colors = ['#09152F','#1D0E58','#621282','#AE138A','#DD1346','#F25D2C,', '#F8D254','#D8FC7D','#BAFFA8','#D6FFE3']

    // make title
    svg.append('text')
    .attr('y', -height/2 + margin.top + 20)
    .attr('text-anchor', 'middle')
    .text(`Top Polluting Industries and Pollutants in ${d_select.state}`)

    // add the groups on the outer part of the circle
    var group = svg
        .append("g")
        .selectAll("g")
        .data(chords.groups)

    // make outer arcs
    group
    .enter()
    .append("g")
    .append("path")
    .style("fill", function(d, i) {
        // only  color in nodes for industries
        return i < naics.length / 2 ? colors[d.index] : 'grey'
    })
    .style("stroke", "black")
    .attr("id", function(d, i) { return "group" + d.index; })
    .attr("d", arc)

    // Add the links between groups
    svg
    .append("g")
    .selectAll("path")
    .data(chords)
    .enter()
    .append("path")
    .attr("d", ribbon)
    .attr('fill-opacity', 0.75)
    .style("fill", function(d) { 
        return colors[d.source.index] // "#69b3a2"
        })
    .style("stroke", "black")
    .style('mix-blend-mode', 'multiply')
    .append('title')
    .text(d => `${naics[d.source.index]} emits ${formatNumber(d.source.value.toFixed(2))} Tonnes ${pollutants[d.target.index]}`)
    .on("mouseover", showTooltip )
    .on("mouseleave", hideTooltip )

    }

// format number for display, since we have numbers of wildly different orders of magnitude
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    } else {
        return num;
    }
    }

// A function that change this tooltip when the user hover a point.
// Its opacity is set to 1: we can now see it. Plus it set the text and position of tooltip depending on the datapoint (d)
var showTooltip = function(d) {
        tooltip
        .style("opacity", 1)
        //.html(`Source: ${naics[d.source.index]}<br>Target: ${pollutants[d.target.index]}`)
        .style("left", (d3.event.pageX + 15) + "px")
        .style("top", (d3.event.pageY - 28) + "px")
    }

// A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
var hideTooltip = function(d) {
    tooltip
    .transition()
    .duration(100)
    .style("opacity", 0)
    }
