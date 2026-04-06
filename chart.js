d3.csv("ds4200_final_data.csv").then(function(data) {

  console.log(Object.keys(data[0]));

  data.forEach(d => d["Anxiety Disorders"] = +d["Anxiety Disorders"]);

  const byCountry = d3.rollup(data,
    v => d3.max(v, d => d["Anxiety Disorders"]),
    d => d.Country
  );

  const top10 = Array.from(byCountry, ([Country, value]) => ({ Country, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  const margin = { top: 60, right: 30, bottom: 80, left: 70 };
  const width  = 800 - margin.left - margin.right;
  const height = 500 - margin.top  - margin.bottom;

  const svg = d3.select("#chart")
    .append("svg")
    .attr("width",  width  + margin.left + margin.right)
    .attr("height", height + margin.top  + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Scales
  const x = d3.scaleBand()
    .domain(top10.map(d => d.Country))
    .range([0, width])
    .padding(0.2);

  const y = d3.scaleLinear()
    .domain([0, d3.max(top10, d => d.value) * 1.1])
    .range([height, 0]);

  // Bars
  svg.selectAll(".bar")
    .data(top10)
    .join("rect")
    .attr("class", "bar")
    .attr("x", d => x(d.Country))
    .attr("width", x.bandwidth())
    .attr("y", d => y(d.value))
    .attr("height", d => height - y(d.value))
    .attr("fill", "#2171b5");

  // X axis
  svg.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-30)")
    .style("text-anchor", "end");

  // Y axis
  svg.append("g")
    .call(d3.axisLeft(y));

  // X label
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height + 70)
    .attr("text-anchor", "middle")
    .style("font-size", "14px")
    .text("Country");

  // Y label
  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", -55)
    .attr("text-anchor", "middle")
    .style("font-size", "14px")
    .text("Percentage of Anxiety Disorders");

  // Title
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", -20)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text("10 Highest Percentages of Anxiety Disorders per Country");

});