// path to pollutants data
shap_path = '../data/shap_values.csv'

shapMargin = {'top': 50, 'bottom': 50, 'left': 50, 'right': 50}

// Based off this: https://observablehq.com/@d3/directed-chord-diagram/2
// chord chart dimensions
const shapWidth = 300 + shapMargin.left + shapMargin.right
const shapHeight = width + shapMargin.top + shapMargin.bottom


// create chord chart elements
var svgShap= d3.select("#shapPlot")
.append("svg")
    .attr("width", shapWidth)
    .attr("height", shapHeight)
    .append("g")
    .attr("transform", `translate(${margin.left},${height - shapMargin.bottom})`);

var tooltip = d3.select("#shapPlot")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip-chord")

d3.csv(shap_path).then(function(data) {
    // sum all values to get the final predicted value
    data.forEach( function(d) {
        let shapSum = 0
        for (const key in d) {
            if (key != "" && !isNaN(parseFloat(d[key]))) {
                shapSum = d[key]
            }
        }
        d.shapSum = shapSum
    })

    console.log('shap vals:', data)

    // order data by most impact. SHAP typically is ordered by the sum of absolute values.

}).catch(error => console.log(error))

