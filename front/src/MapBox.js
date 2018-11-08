import React, { Component } from "react"
import ReactMapboxGl, { Layer, Feature,} from "react-mapbox-gl";

const Map = ReactMapboxGl({
    accessToken: "pk.eyJ1IjoicGllcnJvdGNvIiwiYSI6ImNqbzc5YjVqODB0Z2Mzd3FxYjVsNHNtYm8ifQ.S_87byMcZ0YDwJzTdloBvw"
  });

class MapBox extends Component {

    constructor(props) {
        super(props)
        this.state = props;
    }

      
    render() {
        return(
        <Map
            style="mapbox://styles/mapbox/outdoors-v9"
            containerStyle={{
            height: "500px",
            width: "800px",
            }}
            zoom = {[7]}
            center = {this.props.stations[0].place} >
                <Layer
                type="circle"
                paint = {{
                    "circle-radius" : 10,
                    "circle-color" : "red"}}
                id="marker" >
                {this.props.stations.map((station, key) => (
                <Feature coordinates={station.place}/>
                ))}
            </Layer>

        </Map>
        )
    }
}

export default MapBox;
