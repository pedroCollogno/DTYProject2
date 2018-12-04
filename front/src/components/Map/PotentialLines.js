import React, { Component } from "react";
import { Feature, Layer } from "react-mapbox-gl";

class PotentialLines extends Component {
    render() {
        console.log(this.props);
        return (
            <Layer
                type="line"
                id={"potential_lines" + this.props.network}
                key={"potential_lines" + this.props.network}
                paint={{
                    "line-color": "grey",
                    "line-dasharray": [10, 5]
                }}>
                {
                    this.props.links.map((link, keyy) =>
                        <Feature coordinates={link} key={keyy}></Feature>
                    )
                }
            </Layer>
        );
    }
}

export default PotentialLines;