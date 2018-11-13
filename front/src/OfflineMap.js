

import React, { Component } from "react"


class OfflineMap extends Component {

    constructor(props) {
        super(props)
        this.state = props;
    }

    render() {
        return (
            <div id="map_container" class="container">
                <iframe title="OpenStreetMap" width="100%" height="500" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=-147.86155700683597%2C-32.141897196425795%2C145.6931304931641%2C77.49371508325324&amp;layer=mapnik"></iframe>
            </div>
        )
    }
}

export default OfflineMap;
