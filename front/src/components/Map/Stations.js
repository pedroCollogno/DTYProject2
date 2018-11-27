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
                    Object.keys(this.props.stations).map((station_id, k) =>
                        <Feature coordinates={[this.props.stations[station_id].coordinates.lng, this.props.stations[station_id].coordinates.lat]} key={100 * this.props.stations[station_id].coordinates.lng + this.props.stations[station_id].coordinates.lat} />
                    )
                }
            </Layer>
        );
    }
}

export default Stations;