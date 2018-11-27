import React, { Component } from "react";
import ReactMapboxGl, { Layer, Marker, Feature, ZoomControl, ScaleControl } from "react-mapbox-gl";
import colormap from "colormap";
import Stations from "./Stations.js";
import stationImage from "./EW_high.png";
import Lines from "./Lines.js";
import { countries, global } from "./style";
import "./MapBox.css";

const Map = ReactMapboxGl({ // Only set in case internet is used, as an optional feature.
    accessToken: "pk.eyJ1IjoicGllcnJvdGNvIiwiYSI6ImNqbzc5YjVqODB0Z2Mzd3FxYjVsNHNtYm8ifQ.S_87byMcZ0YDwJzTdloBvw"
});

class MapBox extends Component {

    constructor(props) {
        super(props);
        this.state = {
            zoom: 4,
            emittors: this.props.emittors,
            networksLabels: Object.keys(this.props.emittors),
            colors: colormap({
                colormap: 'jet',
                nshades: Math.max(Object.keys(this.props.emittors).length, 8),
                format: 'hex',
                alpha: 1
            }),
            style: {
                online: 'mapbox://styles/mapbox/streets-v9',
                offline: global
            },
            networksToggled: {
            },
            highlights: {
            }
        };
        for (let label of Object.keys(this.props.emittors)) {
            this.state.highlights[label] = 0;
        }
        this.mouseEnter = this.mouseEnter.bind(this);
        this.mouseExit = this.mouseExit.bind(this);

    }

    componentWillReceiveProps(nextProps) {
        if (nextProps && nextProps.emittors !== this.props.emittors) {
            let highlights = {};
            for (let label of Object.keys(nextProps.emittors)) {
                highlights[label] = 0;
            }
            this.setState({
                emittors: nextProps.emittors,
                networksLabels: Object.keys(nextProps.emittors),
                colors: colormap({
                    colormap: 'jet',
                    nshades: Math.max(Object.keys(nextProps.emittors).length, 8),
                    format: 'hex',
                    alpha: 1
                }), // once component received new props and has set its state, render component anew with new state.
                highlights: highlights,
                networksToggled: nextProps.networksToggled
            });
        }
    }

    center() {
        let keys = this.state.networksLabels;
        if (keys.length === 0) {
            return [2.33, 48.86]; // centered on Paris
        }
        let firstEmittor = Object.keys(this.props.emittors[keys[0]])[0];
        return [this.props.emittors[keys[0]][firstEmittor].coordinates.lng, this.props.emittors[keys[0]][firstEmittor].coordinates.lat];
    }

    clusterCenter(network) {
        let x = 0;
        let y = 0;
        let count = 0;
        for (let station_id of Object.keys(this.state.emittors[network])) {
            let station = this.state.emittors[network][station_id];
            count += 1;
            x += station.coordinates.lng;
            y += station.coordinates.lat;
        }
        return [x / count, y / count];
    }

    mouseEnter(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 2;
        this.setState({ highlights: highlights });
    }

    mouseExit(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 0;
        this.setState({ highlights: highlights });
    }

    getColor(network) {
        let i = parseInt(network);
        if (this.state.colors[i] != undefined) {
            return this.state.colors[i];
        }
        return "white";
    }


    render() {
        let image = new Image(934, 1321);
        image.src = stationImage;
        let images = ["stationImage", image];
        return (
            <div className="map-container">
                <Map
                    style={this.state.style[this.props.connection]}
                    containerStyle={{
                        height: "100%",
                        width: "100%"
                    }}
                    center={this.center()}>
                    {/* CSS ! */}
                    <div className={"tile is-vertical"} id="showhide">
                        <label className={"checkbox"}>
                            <input type="checkbox" onClick={() => this.props.switchAll(true)} />
                            Show all
                    </label>
                        <label className={"checkbox"}>
                            <input type="checkbox" onClick={() => this.props.switchAll(false)} />
                            Hide all
                    </label>
                    </div>
                    {/* CSS ! */}
                    <Layer id="emittors" type="symbol" layout={{
                        "icon-image": "stationImage",
                        "icon-size": 0.03
                    }} images={images} >
                        {
                            Object.keys(this.props.recStations).map((station, k) =>
                                <Feature coordinates={[this.props.recStations[station].coordinates.lng, this.props.recStations[station].coordinates.lat]} key={100 * this.props.recStations[station].coordinates.lng + this.props.recStations[station].coordinates.lat}></Feature>
                            )
                        }
                    </Layer>                    {
                        this.state.networksLabels.map((network, k) => {
                            let clusterCenter = this.clusterCenter(network);
                            let color = this.getColor(network);
                            return (
                                <div id={"cluster" + k} key={"cluster" + k}>
                                    {this.state.networksToggled[network] &&
                                        <Lines
                                            clusterCenter={clusterCenter} color={color}
                                            network={network} stations={this.state.emittors[network]} />
                                    }
                                    <Layer
                                        id={"center" + network}
                                        type="circle"
                                        onClick={() => { this.props.toggleNetwork(network) }}
                                        paint={{
                                            "circle-color": color,
                                            "circle-radius": 6,
                                            "circle-stroke-width": this.state.highlights["" + network]
                                        }}>
                                        <Feature coordinates={clusterCenter} onClick={() => this.props.toggleNetwork(network)}
                                            onMouseEnter={() => {
                                                if (this.state.emittors[network].length > 1) {
                                                    this.mouseEnter(network)
                                                }
                                            }}
                                            onMouseLeave={() => {
                                                if (this.state.emittors[network].length > 1) {
                                                    this.mouseExit(network)
                                                }
                                            }}></Feature>
                                    </Layer>
                                    {this.state.networksToggled[network] &&
                                        <Stations
                                            stations={this.state.emittors[network]} network={network}
                                            color={color} />
                                    }
                                </div>)
                        })
                    }
                    <ZoomControl></ZoomControl>
                    <ScaleControl></ScaleControl>
                </Map >
            </div >
        )
    }


}
export default MapBox;
