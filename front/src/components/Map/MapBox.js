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
            stations: this.props.stations,
            networksLabels: Object.keys(this.props.stations),
            colors: colormap({
                colormap: 'jet',
                nshades: Math.max(Object.keys(this.props.stations).length, 8),
                format: 'hex',
                alpha: 1
            }),
            style: {
                online: 'mapbox://styles/mapbox/streets-v9',
                offline: countries
            },
            networksToggled: {
            },
            highlights: {
            }
        };
        for (let label of Object.keys(this.props.stations)) {
            this.state.networksToggled[label] = false;
            this.state.highlights[label] = 0;
        }
        this.toggleNetwork = this.toggleNetwork.bind(this);
        this.mouseEnter = this.mouseEnter.bind(this);
        this.mouseExit = this.mouseExit.bind(this);
        this.switchAll = this.switchAll.bind(this);

    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.stations !== this.props.stations) {
            let highlights = {};
            for (let label of Object.keys(nextProps.stations)) {
                highlights[label] = 0;
            }
            this.setState({
                stations: nextProps.stations,
                networksLabels: Object.keys(nextProps.stations),
                colors: colormap({
                    colormap: 'jet',
                    nshades: Math.max(Object.keys(nextProps.stations).length, 8),
                    format: 'hex',
                    alpha: 1
                }), // once component received new props and has set its state, render component anew with new state.
                highlights: highlights
            });
        }
    }

    center() {
        let keys = this.state.networksLabels;
        if (keys.length === 0) {
            return [2.33, 48.86]; // centered on Paris
        }
        return [this.props.stations[keys[0]][0].coordinates.lng, this.props.stations[keys[0]][0].coordinates.lat];
    }

    clusterCenter(network) {
        let x = 0;
        let y = 0;
        let count = 0;
        for (let station of this.state.stations[network]) {
            count += 1;
            x += station.coordinates.lng;
            y += station.coordinates.lat;
        }
        return [x / count, y / count];
    }

    toggleNetwork(network) {
        let toggled = this.state.networksToggled[network];
        let networksToggledCopy = JSON.parse(JSON.stringify(this.state.networksToggled));
        networksToggledCopy[network] = !toggled;
        this.setState({ networksToggled: networksToggledCopy });
        this.props.toggleNetwork(network);
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

    switchAll() {
        let newNetworksToggled = {};
        if (this.props.switch === "Show") {
            for (let network of Object.keys(this.state.stations)) {
                newNetworksToggled[network] = true;
            }
        }
        this.setState({
            networksToggled: newNetworksToggled
        });
        this.props.switchAll(newNetworksToggled);
    }

    render() {
        let image = new Image(934, 1321);
        image.src = stationImage;
        let images = ["stationImage", image];
        return (
            <div className="map-container">
                <div className="field switch-container">
                    <input id="switchAll" type="checkbox" name="switchAll" className="switch is-rtl is-rounded is-outlined is-info" onChange={this.switchAll} />
                    <label htmlFor="switchAll"><strong>{this.props.switch} all</strong></label>
                </div>
                <Map
                    style={this.state.style[this.props.connection]}
                    containerStyle={{
                        height: "100%",
                        width: "100%",
                    }}
                    center={this.center()}>
                    <Layer id="stations" type="symbol" layout={{
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
                                            network={network} stations={this.state.stations[network]} />
                                    }
                                    <Layer
                                        id={"center" + network}
                                        type="circle"
                                        onClick={() => { this.toggleNetwork(network) }}
                                        paint={{
                                            "circle-color": color,
                                            "circle-radius": 6,
                                            "circle-stroke-width": this.state.highlights["" + network]
                                        }}>
                                        <Feature coordinates={clusterCenter} onClick={() => this.toggleNetwork(network)}
                                            onMouseEnter={() => {
                                                if (this.state.stations[network].length > 1) {
                                                    this.mouseEnter(network)
                                                }
                                            }}
                                            onMouseLeave={() => {
                                                if (this.state.stations[network].length > 1) {
                                                    this.mouseExit(network)
                                                }
                                            }}></Feature>
                                    </Layer>
                                    {this.state.networksToggled[network] &&
                                        <Stations
                                            stations={this.state.stations[network]} network={network}
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
