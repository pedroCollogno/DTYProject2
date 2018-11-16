import React, { Component } from "react";
import ReactMapboxGl, { Layer, Marker, Feature} from "react-mapbox-gl";
import colormap from "colormap";
import Stations from "./Stations.js";
import stationImage from "./satellite.png";
import Lines from "./Lines.js";

import "./MapBox.css";

const Map = ReactMapboxGl({ // !! REQUIRES INTERNET CONNECTION !! MapBox API (temporary)
    accessToken: "pk.eyJ1IjoicGllcnJvdGNvIiwiYSI6ImNqbzc5YjVqODB0Z2Mzd3FxYjVsNHNtYm8ifQ.S_87byMcZ0YDwJzTdloBvw"
  });

class MapBox extends Component {

    constructor(props) {
        super(props);
        this.state = {
            stations : this.props.stations,
            networksLabels : Object.keys(this.props.stations),
            colors : colormap({
                colormap: 'jet',
                nshades: Math.max(Object.keys(this.props.stations).length, 8),
                format: 'hex',
                alpha: 1
            })
        };
    }

    componentWillReceiveProps(nextProps) {
        if(nextProps.stations !== this.props.stations) {
            this.setState({
                stations : this.props.stations,
                networksLabels : Object.keys(this.props.stations),
                colors : colormap({
                    colormap: 'jet',
                    nshades: Math.max(Object.keys(this.props.stations).length, 8),
                    format: 'hex',
                    alpha: 1
                })
            });
        }
    }

    center() {
        let keys = this.state.networksLabels;
        if(keys.length === 0) {
            return [2.33, 48.86]; // centered on Paname bb
        }
        return [this.props.stations[keys[0]][0].coordinates.lng, this.props.stations[keys[0]][0].coordinates.lat];
    }

    clusterMarker = (coordinates) => (
        <Marker coordinates={coordinates}>

        </Marker>
        );

    clusterCenter(network) {
        let x = 0;
        let y = 0;
        let count = 0;
        for(let station of this.state.stations[network]) {
            count += 1;
            x += station.coordinates.lng;
            y += station.coordinates.lat;
        }
        return [x / count, y / count];
    }

      
    render() {
        let image = new Image(512, 512);
        image.src = stationImage;
        let images = ["stationImage", image];
        let colors = {}
        let i = 0;
        for(let network of this.state.networksLabels) {
            colors[network] = this.state.colors[i];
            i += 1;
        }
        return(
        <Map
            style="mapbox://styles/mapbox/outdoors-v9"
            containerStyle={{
            height: "500px",
            width: "1000px",
            }}
            zoom = {[6]}
            center = {this.center()} >
            <Layer
                id = "stations"
                type = "symbol"
                layout = {{
                    "icon-image" : "stationImage",
                    "icon-size" : 0.05
                }}
                images = {images} >
                {
                    Object.keys(this.props.recStations).map((station, k) =>
                        <Feature coordinates={[this.props.recStations[station].coordinates.lng, this.props.recStations[station].coordinates.lat]}></Feature>
                    )
                }
            </Layer>
            {
                this.state.networksLabels.map((network, k) => {
                    let clusterCenter = this.clusterCenter(network);
                    return(
                        <div id = {"cluster" + k}>
                            <Lines 
                                clusterCenter = {clusterCenter} color = {colors[network]}
                                network = {network} stations = {this.state.stations[network]} />
                            <Layer
                                id = {"center" + network}
                                type = "circle"
                                paint = {{
                                    "circle-color" : colors[network],
                                    "circle-radius" : 3
                                }}>
                                <Feature coordinates = {clusterCenter} ></Feature>
                            </Layer>
                            <Stations 
                                stations = {this.state.stations[network]} network = {network} color = {this.state.colors[network]} />
                        </div>)
                    })
                }
                )
            }
            


        </Map>
        )
    }
}

export default MapBox;
