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

    center() {
        if(this.props.stations.length == 0) {
            return [2.33, 48.86];
        }
        return [this.props.stations[0].coordinates.lng, this.props.stations[0].coordinates.lat];
    }
      
    render() {
        return(
        <Map
            style="mapbox://styles/mapbox/outdoors-v9"
            containerStyle={{
            height: "500px",
            width: "1000px",
            }}
            zoom = {[6]}
            center = {this.center()} >
                <Layer
                type="circle"
                paint = {{
                    "circle-radius" : 3,
                    "circle-color" : "red"}}
                id="marker" >
                {this.props.stations.map((station, key) => (
                <Feature coordinates={[station.coordinates.lng,station.coordinates.lat] }/>
                ))}
            </Layer>

        </Map>
        )
    }
}

export default MapBox;
