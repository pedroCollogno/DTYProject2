import React, { Component } from "react";
import { Marker, Layer, Feature } from "react-mapbox-gl";

class Stations extends Component {

    render() {
        return (

            <Layer
                type="circle"
                id={"circles" + this.props.network}
                paint={{
                    "circle-color": this.props.color,
                    "circle-radius": 5
                }}>
                {
                    this.props.stations.map((station, k) =>
                        <Feature coordinates={[station.coordinates.lng, station.coordinates.lat]} key={100 * station.coordinates.lng + station.coordinates.lat} />
                    )
                }
            </Layer>
        );
    }
}

export default Stations;