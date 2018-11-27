import React, { Component } from "react";
import { Feature, Layer } from "react-mapbox-gl";

class Lines extends Component {
    render() {
        return (
            <Layer
                type="line"
                id={"lines" + this.props.network}
                key={"lines" + this.props.network}
                paint={{
                    "line-color": this.props.color
                }}>
                {
                    this.props.stations.map((station, k) =>
                        <Feature coordinates={[[station.coordinates.lng, station.coordinates.lat], this.props.clusterCenter]} key={100 * station.coordinates.lng - this.props.clusterCenter[0] + station.coordinates.lat - this.props.clusterCenter[1]} />
                    )
                }
            </Layer>
        );
    }
}

export default Lines;