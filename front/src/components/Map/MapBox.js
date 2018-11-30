import React, { Component } from "react";
import ReactMapboxGl, { Layer, Feature, ZoomControl, ScaleControl } from "react-mapbox-gl";
import colormap from "colormap";
import Stations from "./Stations.js";
import stationImage from "./EW_high.png";
import Lines from "./Lines.js";
import { global } from "./style";
import PropTypes from "prop-types";
import "./MapBox.css";

const Map = ReactMapboxGl({ // Only set in case internet is used, as an optional feature.
    accessToken: "pk.eyJ1IjoicGllcnJvdGNvIiwiYSI6ImNqbzc5YjVqODB0Z2Mzd3FxYjVsNHNtYm8ifQ.S_87byMcZ0YDwJzTdloBvw"
});

class MapBox extends Component {

    constructor(props) {
        super(props);
        this.state = {
            emittors: props.emittors,

            networksLabels: Object.keys(props.emittors), // the networks labels
            colors: colormap({ // a colormap to set a different color for each network
                colormap: 'jet',
                nshades: Math.max(Object.keys(props.emittors).length, 8), // 8 is the minimum number of colors
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
        for (let label of Object.keys(props.emittors)) {
            this.state.highlights[label] = 0; // at the beginning, networks are not hovered over (supposedly)
        }
        this.mouseEnter = this.mouseEnter.bind(this); // allows those functions to update the state of the component 
        this.mouseExit = this.mouseExit.bind(this); // (here, we want to update highlights)

    }

    /**
     * re-renders the map each time it received a new prop (emittor or network toggling)
     * @param {*} nextProps 
     */
    componentWillReceiveProps(nextProps) {
        console.log(nextProps);
        if (nextProps && nextProps !== this.props) { // little check, doesn't hurt
            let highlights = {};
            for (let label of Object.keys(nextProps.emittors)) { // eventual new network, along with all the other ones, is not highlighted
                highlights[label] = 0;
            }
            this.setState({ // updates the state with the new props, thus re-rendering the component
                emittors: nextProps.emittors,
                networksLabels: Object.keys(nextProps.emittors),
                colors: colormap({
                    colormap: 'jet',
                    nshades: Math.max(Object.keys(nextProps.emittors).length, 8),
                    format: 'hex',
                    alpha: 1
                }),
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

    /**
     * returns the geometric center of all the points of the network, for simpler rendering
     * @param {*} network 
     */
    clusterCenter(network) {
        let x = 0;
        let y = 0;
        let stationLabels = Object.keys(this.state.emittors[network]);
        let N = stationLabels.length;
        for (let station_id of stationLabels) {
            let station = this.state.emittors[network][station_id];
            x += station.coordinates.lng;
            y += station.coordinates.lat;
        }
        console.log("Center of network " + network + " is : " + x / N + "," + y / N);
        return [x / N, y / N]; // arithmetic means of the coordinates
    }

    /**
     * when hovering over a network center, highlights it
     * @param {*} network 
     */
    mouseEnter(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 2;
        this.setState({ highlights: highlights });
    }

    /**
     * when the pointer leaves, removes the highlight
     * @param {*} network 
     */
    mouseExit(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 0;
        this.setState({ highlights: highlights });
    }

    /**
     * gets the color of each network (white if null)
     * @param {*} network 
     */
    getColor(network) {
        let i = parseInt(network);
        if (i < 0) {
            console.log("Unidentified network");
            return "grey";
        }
        if (this.state.colors[i] != undefined) {
            return this.state.colors[i];
        }
        console.log("Color " + network + " is undefined");
        return "white";
    }

    render() {
        let image = new Image(934, 1321); // image for the stations
        image.src = stationImage;
        let images = ["stationImage", image]; // sets it as a source for the map
        return (
            <div className="map-container">
                {/* the map contains everything (because it implements the actual HTML canvas) */}
                <Map
                    style={this.state.style[this.props.connection]}
                    // online or offline
                    containerStyle={{
                        height: "100%",
                        width: "100%"
                    }}
                // where the map is centered when rendering /!\ ATTENTION : enlever si trop chiant /!\
                // center={this.center()}
                >

                    <div className={"tile is-vertical"} id="showhide">
                        {/* The checkboxes to hide/show everything */}
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

                    <Layer id="recStations" type="symbol" layout={{
                        "icon-image": "stationImage",
                        "icon-size": 0.03
                    }} images={images} >
                        {/* Displays the reception stations as images using the previously defined source image */}
                        {
                            Object.keys(this.props.recStations).map((station, k) =>
                                <Feature coordinates={[this.props.recStations[station].coordinates.lng, this.props.recStations[station].coordinates.lat]} key={100 * this.props.recStations[station].coordinates.lng + this.props.recStations[station].coordinates.lat}></Feature>
                            )
                        }
                    </Layer>
                    {
                        this.state.networksLabels.map((network, k) => {
                            // Displays every network using 3 Layers : "center" which contains only the center of the
                            // network, Stations which contains all the actual emittors of the network and Lines which
                            // contains the connections between each node of the network.
                            // Those last 2 are rendered uniquely when toggled or if showAll is active.
                            let clusterCenter = this.clusterCenter(network);
                            let color = this.getColor(network);
                            let toggled = this.state.networksToggled[network];
                            toggled = !(toggled == undefined || !toggled);
                            toggled = !this.props.hideAll && (toggled || this.props.showAll);
                            let lines = toggled && (network != "-1000");
                            // toggled is True iff it's defined, not manually de-toggled (= False) and hideAll is not active
                            // or simply if showAll is active

                            return (
                                <div id={"cluster" + k} key={"cluster" + k}>
                                    {lines &&// conditionnal rendering
                                        <Lines
                                            clusterCenter={clusterCenter} color={color}
                                            network={network} stations={this.state.emittors[network]} />
                                    }
                                    {network != "-1000" &&
                                        <Layer
                                            // always rendering
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
                                                        // if there is only one emittor in the network, the center is actually the node
                                                        this.mouseEnter(network);
                                                    }
                                                }}
                                                onMouseLeave={() => {
                                                    if (Object.keys(this.state.emittors[network]).length > 1) {
                                                        // same here
                                                        this.mouseExit(network);
                                                    }
                                                }}></Feature>
                                        </Layer>
                                    }
                                    {toggled && // conditionnal rendering
                                        <Stations
                                            stations={this.state.emittors[network]} network={network}
                                            color={color} />
                                    }
                                </div>)
                        })
                    }
                    {/* Gadgets */}
                    <ZoomControl></ZoomControl>
                    <ScaleControl></ScaleControl>
                </Map >
            </div >
        )
    }


}

MapBox.propTypes = {
    /**
     * the emittors received from App.js, in the form :
     *   {    network_id : {
     *           emittor_id : {
     *               coordinates : {lat : float, lng : float}, ...
     *           }
     *       }
     *   }
     */
    emittors: PropTypes.objectOf(PropTypes.objectOf(PropTypes.object)).isRequired,
    /**
     * the list of the reception stations
     */
    recStations: PropTypes.objectOf(PropTypes.objectOf(PropTypes.object)).isRequired,
    /**
     * the connection status
     */
    connection: PropTypes.oneOf(["online", "offline"]).isRequired,
    /**
     * the function to call when toggling a network
     */
    toggleNetwork: PropTypes.func.isRequired,
    /**
     * is the showAll button checked ?
     */
    showAll: PropTypes.bool.isRequired,
    /**
     * is the hideAll button checked ?
     */
    hideAll: PropTypes.bool.isRequired,
    /**
     * the function to toggle showAll (if called with True) or hideAll (if called with False)
     * @param : {Boolean} all Whether to change showAll of hideAll
     */
    switchAll: PropTypes.func.isRequired,
    /**
     * the networks toggled/de-toggled manually by the user so far
     */
    networksToggled: PropTypes.objectOf(PropTypes.bool).isRequired

}


export default MapBox;

