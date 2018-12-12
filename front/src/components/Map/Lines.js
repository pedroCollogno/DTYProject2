import React, { Component } from "react";
import { Feature, Layer } from "react-mapbox-gl";
import PropTypes from "prop-types";

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

Lines.propTypes = {
    /**
     * the stations of the network to display
     */
    stations: PropTypes.objectOf(PropTypes.object).isRequired,
    /**
     * the network id, for proper Layer id-ing
     */
    network: PropTypes.string.isRequired,
    /**
     * the color of the lines
     */
    color: PropTypes.string.isRequired
}

export default Lines;