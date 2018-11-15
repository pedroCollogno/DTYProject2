import React, { Component } from "react";
import { Marker } from "react-mapbox-gl";

class Station extends Component {
    constructor(props) {
        super(props);
        this.state = {
            coordinates : [props.coordinates.lng, props.coordinates.lng],
            color : props.color,
            type : props.type
        }
    }

    render() {
        return(
            <Marker
                coordinates = { this.state.coordinates }>
                <div className = {this.state.type} style = {{"backgroundColor" : this.state.color}}></div>
            </Marker>
        );
    }
}

export default Station;