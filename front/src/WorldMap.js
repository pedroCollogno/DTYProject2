import React, { Component } from "react"
import { geoMercator, geoPath } from "d3-geo"
import { feature } from "topojson-client"
let world = require("./world-110m.json")

class WorldMap extends Component {
  constructor() {
    super()
    this.state = {
      worldData: []
    }
  }
  projection() {
    return geoMercator()
      .scale(100)
      .translate([ 1000 / 2, 600 / 2 ])
  }

  afficheStation(station){
    console.log(station);
  }


  componentDidMount() {
    
    this.setState({
      worldData: feature(world, world.objects.countries).features,
    })
  }





  render() {
    return (
      <svg width={ 1000 } height={ 600 } viewBox="0 0 1000 600">
        <g className="countries">
          {
            this.state.worldData.map((d,i) => (
              <path
                key={ `path-${ i }` }
                d={ geoPath().projection(this.projection())(d) }
                className="country"
                fill={ `rgba(38,50,56,${1 / this.state.worldData.length * i})` }
                stroke="#FFFFFF"
                strokeWidth={ 0.5 }
              />
            ))
          }
        </g>
        <g className="markers">
        {this.props.stations.map( (station, index) => (
          <circle id={station.id} onClick={() => this.afficheStation(station)}
            cx={ this.projection()(station.place)[0] }
            cy={ this.projection()(station.place)[1] }
            r={ 5 }
            fill="#E91E63"
            className="marker"
          />
         ))}
        </g>
      </svg>
    )
  }
}

export default WorldMap