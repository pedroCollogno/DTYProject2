import React, { Component } from "react";
import ReactMapboxGl, { Layer, Feature, ZoomControl, ScaleControl } from "react-mapbox-gl";
import colormap from "colormap";
import Stations from "./Stations.js";
import recImage from "./EW_high.png";
import centerImage from "./dashed-circle.png";
import Lines from "./Lines.js";
import PotentialLines from "./PotentialLines.js";
import { global } from "./style";
import PropTypes from "prop-types";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

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
            },
            nameNets: false
        };
        for (let label of Object.keys(props.emittors)) {
            this.state.highlights[label] = 0; // at the beginning, networks are not hovered over (supposedly)
        }
        this.mouseEnter = this.mouseEnter.bind(this); // allows those functions to update the state of the component 
        this.mouseExit = this.mouseExit.bind(this); // (here, we want to update highlights)
        this.center = this.center.bind(this);
        this.nameNetworks = this.nameNetworks.bind(this);
    }

    /**
     * re-renders the map each time it received a new prop (emittor or network toggling)
     * @param {*} nextProps 
     */
    componentWillReceiveProps(nextProps) {
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
                networksToggled: nextProps.networksToggled,
                white: nextProps.white
            });
        }
    }

    /**
     * Centers the map on a "relevant" point (Paris by default, the first emittor if .PRP files have already been uploaded)
     */
    center() {
        let keys = this.state.networksLabels;
        if (keys.length === 0) {
            this.map.state.map.flyTo({ center: [2.33, 48.86] }); // centered on Paris if no emittor to display
        }
        let firstEmittor = Object.keys(this.props.emittors[keys[0]])[0]; // else, centered on the very first emittor received
        this.map.state.map.flyTo({ center: [this.props.emittors[keys[0]][firstEmittor].coordinates.lng, this.props.emittors[keys[0]][firstEmittor].coordinates.lat] });
    }

    /**
     * Returns the geometric center of all the points of the network, for simpler rendering
     * @param {String} network 
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
        return [x / N, y / N]; // arithmetic means of the coordinates
    }

    /**
     * When hovering over a network center, highlights it
     * @param {String} network 
     */
    mouseEnter(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 2;
        this.setState({ highlights: highlights });
    }

    /**
     * when the pointer leaves, removes the highlight
     * @param {String} network 
     */
    mouseExit(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 0;
        this.setState({ highlights: highlights });
    }

    /**
     * gets the color of each network (white if null)
     * @param {String} network 
     */
    getColor(network) {
        let networkNumber = parseInt(network);
        if (networkNumber < 0) {
            console.log("Unidentified network");
            return "#5c5c5c";
        }
        if (this.state.colors[networkNumber] != undefined) {
            return this.state.colors[networkNumber];
        }
        console.log("Color " + network + " is undefined");
        return "#ffffff";
    }

    /**
     * Toggles between the network names and their emittors numbers (triggered when clicking the "labels" button)
     */
    nameNetworks() {
        this.setState({ nameNets: !this.state.nameNets });
    }

    render() {
        let htmlRecImage = new Image(934, 1321); // image for the reception stations
        htmlRecImage.src = recImage; // HTML format to render it in the canvas
        let htmlCenterImage = new Image(256, 256); // image for the network centers 
        htmlCenterImage.src = centerImage;

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
                    ref={(e) => { this.map = e; }} // Allows direct references to the map (and thus direct actions e.g. "map.flyTo()")
                    onStyleLoad={(map) => { // Adds the HTML images as sources for later use in Layer components
                        map.addImage("recStation", htmlRecImage); // The reference name for this image
                        map.addImage("networkCenter", htmlCenterImage);
                    }}
                >

                    <div id="showhide">
                        {/* The checkboxes to hide/show everything */}
                        <div className="field">
                            <input className="is-checkradio is-block" type="checkbox" id="show_checkbox" name="show_checkbox" checked={this.props.showVal} onChange={this.props.changeShowVal} onClick={() => this.props.switchAll(true)} />
                            <label htmlFor="show_checkbox">
                                <span> </span>Show all
                            </label>
                        </div>
                        <div className="field">
                            <input className="is-checkradio is-block" type="checkbox" id="hide_checkbox" name="hide_checkbox" checked={this.props.hideVal} onChange={this.props.changeHideVal} onClick={() => this.props.switchAll(false)} />
                            <label htmlFor="hide_checkbox">
                                <span> </span>Hide all
                            </label>
                        </div>
                    </div>

                    <Layer id="recStations" key="recStations" type="symbol" layout={{
                        "icon-image": "recStation",
                        "icon-size": 0.03
                    }}>
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
                            let clusterCenter = this.clusterCenter(network); // the center coordinates
                            let color = this.getColor(network); // the color of the network
                            let emittors = this.state.emittors[network]; // al the emittors in this network
                            let emittorsNumber = Object.keys(emittors).length;
                            let toggled = this.state.networksToggled[network];
                            toggled = !(toggled == undefined || !toggled);
                            toggled = !this.props.hideAll && (toggled || this.props.showAll);
                            toggled = (emittorsNumber == 1) || toggled;
                            // toggled is True if it's defined, not manually de-toggled (= False) and hideAll is not active
                            // or simply if showAll is active. Single emittors are always displayed.

                            let lines = toggled && (network != "-1000"); // We show the lines if the network is toggled.
                            // At the beginning, no line should be shown (the emittors are shown as a cloud of unconnected points).

                            let potentialLinks = []; // When using both ML and DL : list of all the corrected potential links given by the DL
                            Object.keys(emittors).map((track_id, keyy) => {
                                let potentialNetwork = emittors[track_id]["possible_network"];
                                if (potentialNetwork != undefined && potentialNetwork != network) { // If there was a match with another network...
                                    potentialLinks.push([[emittors[track_id]["coordinates"]["lng"], emittors[track_id]["coordinates"]["lat"]],
                                    this.clusterCenter(potentialNetwork)]); // ...the link between the emittors coordinates and the other network's center's coordiantes is saved.
                                }
                            });

                            let showPotential = (toggled && potentialLinks.length != 0); // We only
                            let textCenter = "" + emittorsNumber;
                            if (this.state.nameNets) {
                                textCenter = "" + (parseInt(network) + 1);
                            }
                            return (
                                <div id={"cluster" + k} key={"cluster" + k}>
                                    {lines &&// conditionnal rendering
                                        <Lines
                                            clusterCenter={clusterCenter} color={color}
                                            network={network} stations={emittors} />
                                    }
                                    {network != "-1000" && emittorsNumber > 1 && !toggled && // always rendering when simulation has started
                                        <Layer
                                            id={"center" + network}
                                            key={"center" + network}
                                            type="symbol"
                                            onClick={() => { this.props.toggleNetwork(network) }}
                                            layout={{
                                                "text-field": textCenter,
                                                "text-size": 19,
                                                "icon-image": "networkCenter",
                                                "icon-size": 0.1,
                                                "icon-allow-overlap": true,
                                                "text-allow-overlap": true,
                                                "text-font": ["Open Sans Regular"],
                                            }} paint={{
                                                "text-color": this.getColor(network),
                                                "text-halo-color": "black",
                                                "text-halo-width": 0.1 + this.state.highlights["" + network],
                                            }}

                                        >
                                            <Feature coordinates={clusterCenter} onClick={() => this.props.toggleNetwork(network)}
                                                onMouseEnter={() => this.mouseEnter(network)}
                                                onMouseLeave={() => this.mouseExit(network)}
                                                key={"featureCenter" + network}
                                            ></Feature>
                                        </Layer>
                                    }

                                    {network != "-1000" && emittorsNumber > 1 && toggled && // always rendering when simulation has started
                                        <Layer
                                            id={"centerToggled" + network}
                                            key={"centerToggled" + network}
                                            type="circle"
                                            onClick={() => { this.props.toggleNetwork(network) }}
                                            paint={{
                                                "circle-color": this.getColor(network),
                                                "circle-radius": 3,
                                                "circle-stroke-width": this.state.highlights["" + network]
                                            }}

                                        >
                                            <Feature coordinates={clusterCenter} onClick={() => this.props.toggleNetwork(network)}
                                                onMouseEnter={() => this.mouseEnter(network)}
                                                onMouseLeave={() => this.mouseExit(network)}
                                                key={"featureCenterToggled" + network}
                                            ></Feature>
                                        </Layer>
                                    }

                                    {toggled && // conditionnal rendering
                                        <Stations
                                            stations={emittors} network={network}
                                            color={color} multiple={emittorsNumber > 1}
                                            white={this.props.white} />
                                    }
                                    {showPotential &&
                                        <PotentialLines
                                            links={potentialLinks}
                                            network={network} />
                                    }
                                </div>)
                        })
                    }
                    {/* Widgets */}
                    <div className="widgets">
                        <a id="center-button" onClick={this.center}>
                            <span className="icon">
                                <FontAwesomeIcon icon='location-arrow' />
                            </span>
                        </a>
                    </div>
                    <ZoomControl></ZoomControl>
                    <ScaleControl></ScaleControl>
                    <div className="widgets-tag">
                        <a id="network-names-button" onClick={this.nameNetworks}>
                            <span className="icon">
                                <FontAwesomeIcon icon='tags' />
                            </span>
                        </a>
                    </div>

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

