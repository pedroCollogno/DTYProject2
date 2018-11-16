import React, { Component } from "react";
import { Marker } from "react-mapbox-gl";

class Stations extends Component {

    render() {
        return(
            <div>
                {
                    this.props.stations.map((station, key) =>(
                        // let geojson = {
                        //     "type": "Featurecollection",
                        //     "features": [{
                        //     "type": "Feature",
                        //     "geometry" : {
                        //         "type" : "LineString",
                        //         "coordinates": [
                        //             [station.coordinates.lng, station.coordinates.lat],
                        //             clusterCenter
                        //             ]
                        //         }
                        //     }],
                        // };
                        // console.log(geojson);
                                <Marker
                                    key = {key}
                                    coordinates = { [station.coordinates.lng, station.coordinates.lat] }>
                                    <div className = "mapMarker" style = {{"backgroundColor" : this.props.color}}></div>
                                </Marker>
                        ))
                }
            </div>
        );
    }
}

export default Stations;