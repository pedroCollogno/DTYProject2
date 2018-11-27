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
                    Object.keys(this.props.stations).map((station_id, k) =>
                        <Feature coordinates={[[this.props.stations[station_id].coordinates.lng, this.props.stations[station_id].coordinates.lat], this.props.clusterCenter]} key={100 * this.props.stations[station_id].coordinates.lng - this.props.clusterCenter[0] + this.props.stations[station_id].coordinates.lat - this.props.clusterCenter[1]} />
                    )
                }
            </Layer>
        );
    }
}

export default Lines;