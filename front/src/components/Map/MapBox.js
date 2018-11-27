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
            emittors: this.props.emittors,
            // the emittors received from App.js, in from of : {
            //     network_id : {
            //         emittor_id : {
            //             coordinates : {lat : float, lng : float}, ...
            //         }
            //     }
            // }
            networksLabels: Object.keys(this.props.emittors), // the networks labels
            colors: colormap({ // a colormap to set a differnet color for each network
                colormap: 'jet',
                nshades: Math.max(Object.keys(this.props.emittors).length, 8), // 8 is the minimum number of colors
                format: 'hex',
                alpha: 1 // opacity
            }),
            style: {
                online: 'mapbox://styles/mapbox/streets-v9', // if "online" is toggled, renders map through the Web (OpenStreet Map)
                offline: global // else, renders the local version of the map (pre-dowloaded tiles for different levels of zoom)
            },
            networksToggled: { // the networks to display (by default, only one "center" is displayed for better visualization)
            },
            highlights: { // the networks that are hovered over
            }
        };
        for (let label of Object.keys(this.props.emittors)) {
            this.state.highlights[label] = 0; // at the beginning, networks are not hovered over (supposedly)
        }
        this.mouseEnter = this.mouseEnter.bind(this); // allows those functions to update the state of the component 
        this.mouseExit = this.mouseExit.bind(this);

    }

    componentWillReceiveProps(nextProps) { // re-renders the map each time it received a new prop (emittor or network toggling)
        if (nextProps && nextProps !== this.props) { // little check
            let highlights = {};
            for (let label of Object.keys(nextProps.emittors)) { // eventual new network, along with all the other ones, is not highlighted
                highlights[label] = 0;
            }
            this.setState({ // update the state with the new props, thus re-rendering the component
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

    center() { // N.B. : a revoir, super chiant sa race
        let keys = this.state.networksLabels;
        if (keys.length === 0) {
            return [2.33, 48.86]; // centered on Paris if no emittor to display
        }
        let firstEmittor = Object.keys(this.props.emittors[keys[0]])[0]; // else, centered on the very first emittor received
        return [this.props.emittors[keys[0]][firstEmittor].coordinates.lng, this.props.emittors[keys[0]][firstEmittor].coordinates.lat];
    }

    clusterCenter(network) { // returns the geometric center of all the points of the network, for simpler rendering
        let x = 0;
        let y = 0;
        let count = 0;
        for (let station_id of Object.keys(this.state.emittors[network])) {
            let station = this.state.emittors[network][station_id];
            count += 1;
            x += station.coordinates.lng;
            y += station.coordinates.lat;
        }
        return [x / count, y / count]; // arithmetic means
    }

    mouseEnter(network) { // when hovering over a network center, highlights it
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 2;
        this.setState({ highlights: highlights });
    }

    mouseExit(network) { // when leaving, removing the highlight
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 0;
        this.setState({ highlights: highlights });
    }

    getColor(network) { // gets the color of each network (white if null)
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
                            <strong>  </strong>Show all
                    </label>
                        <label className={"checkbox"}>
                            <input type="checkbox" onClick={() => this.props.switchAll(false)} />
                            <strong>  </strong>Hide all
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
                            let toggled = this.state.networksToggled[network];
                            toggled = !(toggled == undefined || !toggled);
                            toggled = !this.props.hideAll && (toggled || this.props.showAll);
                            console.log("Network : " + network + " Toggeld : " + toggled);
                            return (
                                <div id={"cluster" + k} key={"cluster" + k}>
                                    {toggled &&
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
                                                if (Object.keys(this.state.emittors[network]).length > 1) {
                                                    this.mouseEnter(network)
                                                }
                                            }}
                                            onMouseLeave={() => {
                                                if (Object.keys(this.state.emittors[network]).length > 1) {
                                                    this.mouseExit(network)
                                                }
                                            }}></Feature>
                                    </Layer>
                                    {toggled &&
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
