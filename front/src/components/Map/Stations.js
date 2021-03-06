import React, { Component } from "react";
import { Layer, Feature } from "react-mapbox-gl";
import PropTypes from "prop-types";

class Stations extends Component {

    fade(color) {
        color = color.slice(1);
        let r = parseInt(color.slice(0, 2), 16);
        let g = parseInt(color.slice(2, 4), 16);
        let b = parseInt(color.slice(4, 6), 16);
        return ("rgba(" + r + "," + g + "," + b + ",0.3)");
    }

    getColor(station) {
        let properties = { "color": this.props.color, "border": "rgba(0,0,0,0)" };
        if (station.talking == undefined || !station.talking) {
            properties["color"] = this.fade(this.props.color);
        }
        if (station["track_id"] == this.props.white) {
            properties["border"] = "white";
        }
        return properties;
    }

    render() {
        if (this.props.multiple) {
            return (
                <Layer
                    type="circle"
                    id={"circles" + this.props.network}
                    key={"circles" + this.props.network}
                    paint={{
                        "circle-color": ["get", "color"],
                        "circle-radius": 6,
                        "circle-stroke-width": 4,
                        "circle-stroke-color": ["get", "border"],
                    }}>
                    {
                        Object.keys(this.props.stations).map((station_id, k) =>
                            <Feature coordinates={[this.props.stations[station_id].coordinates.lng, this.props.stations[station_id].coordinates.lat]} key={100 * this.props.stations[station_id].coordinates.lng + this.props.stations[station_id].coordinates.lat}
                                properties={this.getColor(this.props.stations[station_id])} />
                        )
                    }
                </Layer>
            );
        }
        return (
            <Layer
                type="circle"
                id={"circles" + this.props.network}
                key={"circles" + this.props.network}
                paint={{
                    "circle-stroke-color": ["get", "color"],
                    "circle-radius": 5,
                    "circle-stroke-width": 4,
                    "circle-color": ["get", "border"]
                }}>
                {
                    Object.keys(this.props.stations).map((station_id, k) =>
                        <Feature coordinates={[this.props.stations[station_id].coordinates.lng, this.props.stations[station_id].coordinates.lat]} key={100 * this.props.stations[station_id].coordinates.lng + this.props.stations[station_id].coordinates.lat}
                            properties={this.getColor(this.props.stations[station_id])} />
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