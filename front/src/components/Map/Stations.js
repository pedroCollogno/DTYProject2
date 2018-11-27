import React, { Component } from "react";
import { Layer, Feature } from "react-mapbox-gl";
import PropTypes from "prop-types";

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

Stations.propTypes = {
    /**
     * the stations of the network to display
     */
    stations: PropTypes.objectOf(PropTypes.object).isRequired,
    /**
     * the network id, for proper Layer id-ing
     */
    network: PropTypes.string.isRequired,
    /**
     * the color of the nodes
     */
    color: PropTypes.string.isRequired
}

export default Stations;