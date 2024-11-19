// path to pollutants data
data_path = '../data/states_pollution_dense.json'

margin = {'top': 50, 'bottom': 50, 'left': 50, 'right': 50}

// Based off this: https://observablehq.com/@d3/directed-chord-diagram/2
// chord chart dimensions
const width = 300 + margin.left + margin.right
const height = width + margin.top + margin.bottom
const innerRadius = Math.min(width, height) * 0.5 - margin.top
const outerRadius = innerRadius + 10

// create chord chart elements
var svgChord = d3.select("#chordChart")
.append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width/2},${height/2})`);

var tooltip = d3.select("#chordChart")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip-chord")

var colors = ['#09152F','#1D0E58','#621282','#AE138A','#DD1346','#F25D2C,', '#F8D254','#D8FC7D','#BAFFA8','#D6FFE3']

var dropDown = d3.select('body')
                .select('select.pollutants');

d3.json(data_path).then(function(data) {

    console.log(data)

    dropDownOptions = Object.keys(data[0]).filter(d => d != 'state')

    // populate dropdown
    dropDown.selectAll('option')
            .data(dropDownOptions)
            .enter()
            .append('option')
            .attr('value', d => d)
            .text(d => d)

    var defaultPollutant = d3.select('select.pollutants').node().value

    createChordChart(svgChord, data, 'USA', defaultPollutant)

    // event listener to change dropdown
    d3.select('select.pollutants')
        .on('change', function() {
                svgChord.selectAll("*").remove()

                createChordChart(svgChord, data, 'USA', d3.select(this).property('value'))
                })

}).catch(error => console.log(error))

function createChordChart(svg, emissionsData, state, pollutantSelection) {
    // clear existing elements
    svg.selectAll("*").remove();

    let d_select = emissionsData.find(d => d.state === state)
    
    console.log('fn test', pollutantSelection)

    matrix = d_select[pollutantSelection].data
    naics = d_select[pollutantSelection].index
    pollutants = d_select[pollutantSelection].columns

    let chord = d3.chordDirected()
        .padAngle(12 / innerRadius)

    let chords = chord(matrix);

    let arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    let ribbon = d3.ribbonArrow()
        .radius(innerRadius - 0.5)
        .padAngle(1 / innerRadius);

    // make title
    svg.append('text')
    .attr('y', -height/2 + margin.top + 20)
    .attr('dy', '0em')
    .attr('text-anchor', 'middle')
    .text(`Top Industry Polluters in ${d_select.state}`)
    .append('text')
    .attr('dy', '1em')
    .text(pollutantSelection)

    // add the groups on the outer part of the circle
    var group = svg
        .append("g")
        .selectAll("g")
        .data(chords.groups)

    // make outer arcs
    group.enter()
        .append("g")
        .append("path")
        .style("fill", function(d, i) {
            // only  color in nodes for industries
            return i < naics.length / 2 ? colors[d.index] : 'grey'
        })
        .style("stroke", "black")
        .attr("id", function(d, i) { return "group" + d.index; })
        .attr("d", arc)
        .on("mouseover", function(event, d) {
            d3.select(this)
            .style('fill', '#ADD8E6')

            var t = `${naics[d.index]} Total Emissions: ${formatNumber(d.value)} Tonnes`
            showTooltip(event, t)
        })
        .on("mouseleave", function(event, d) {
            d3.select(this)
            .style('fill', d.index < 10 ? colors[d.index] : 'grey')

            hideTooltip(d)
        })

    // Add the links between groups
    svg.append("g")
        .attr('id', 'innerFlows')
        .selectAll("path")
        .data(chords)
        .enter()
        .append("path")
        .attr("d", ribbon)
        .attr('fill-opacity', 0.75)
        .style("fill", function(d) { 
            return colors[d.source.index]
            })
        .style("stroke", "black")
        .style('mix-blend-mode', 'multiply')
        .on("mouseover", function(event, d) {
            d3.select(this)
            .style('fill', '#ADD8E6')
            .style('fill-opacity', 0.45)

            var t = `${naics[d.source.index]} emits ${formatNumber(d.source.value.toFixed(2))} Tonnes ${pollutants[d.target.index]}`
            showTooltip(event, t)
        })
        .on("mouseleave", function(event, d) {
            d3.select(this)
            .style('fill', colors[d.source.index])
            .style('fill-opacity', 0.75)

            hideTooltip(d)
        })

        // Set the zoom and Pan features: how much you can zoom, on which part, and what to do when there is a zoom
        var zoom = d3.zoom()
        .scaleExtent([.5, 20])  // This control how much you can unzoom (x0.5) and zoom (x20)
        .extent([[0, 0], [width, height]])

    }

// format number for display, since we have numbers of wildly different orders of magnitude
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    } else {
        return (num / 1).toFixed(1);
    }
    }

// A function that change this tooltip when the user hover a point.
// Its opacity is set to 1: we can now see it. Plus it set the text and position of tooltip depending on the datapoint (d)
var showTooltip = function(event, htmlTxt) {
        tooltip
        .style("opacity", 1)
        .html(htmlTxt)
        .style("left", (event.pageX + 15) + "px")
        .style("top", (event.pageY - 28) + "px")
    }

// A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
var hideTooltip = function(d) {
    tooltip
    .style("opacity", 0)
    }
