import React, { Component } from "react";
import ReactMapboxGl, { Layer, Feature, ZoomControl, ScaleControl } from "react-mapbox-gl";
import Stations from "./Stations.js";
import recImage from "./EW_high.png";
import lineImage from "./line.png";
import dashImage from "./dashed_line.png";
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

let htmlRecImage = new Image(467, 314); // image for the reception stations
htmlRecImage.src = recImage; // HTML format to render it in the canvas
let htmlCenterImage = new Image(256, 256); // image for the network centers 
htmlCenterImage.src = centerImage;

class MapBox extends Component {

    constructor(props) {
        super(props);
        let labels = Object.keys(props.emitters);
        this.state = {
            emitters: props.emitters,

            networksLabels: labels, // the networks labels
            style: {
                online: 'mapbox://styles/mapbox/streets-v9', // if "online" is toggled, renders map through the Web (OpenStreet Map)
                offline: global // else, renders the local version of the map (pre-dowloaded tiles for different levels of zoom)
            },
            networksToggled: { // the networks to display (by default, only one "center" is displayed for better visualization)
            },
            highlights: { // the networks that are hovered over
            },
            nameNets: false,
            legend: false
        };
        for (let label of labels) {
            this.state.highlights[label] = 0; // at the beginning, networks are not hovered over (supposedly)
        }
        this.mouseEnter = this.mouseEnter.bind(this); // allows those functions to update the state of the component 
        this.mouseExit = this.mouseExit.bind(this); // (here, we want to update highlights)
        this.center = this.center.bind(this);
        this.nameNetworks = this.nameNetworks.bind(this);
        this.toggle_legend = this.toggle_legend.bind(this);
    }

    /**
     * Re-renders the map each time it received a new prop (emitter or network toggling)
     * @param {*} nextProps 
     */
    componentWillReceiveProps(nextProps) {
        if (nextProps && nextProps !== this.props) { // little check, doesn't hurt
            let highlights = {};
            let labels = Object.keys(nextProps.emitters);
            for (let label of labels) { // eventual new network, along with all the other ones, is not highlighted
                highlights[label] = 0;
            }

            this.setState({ // updates the state with the new props, thus re-rendering the component
                emitters: nextProps.emitters,
                networksLabels: labels,
                highlights: highlights,
                networksToggled: nextProps.networksToggled,
                white: nextProps.white,
                colors: nextProps.colors
            });
        }
    }

    /**
     * Centers the map on a "relevant" point (Paris by default, the first emitter if .PRP files have already been uploaded)
     */
    center() {
        let keys = this.state.networksLabels;
        if (keys.length === 0) {
            this.map.state.map.flyTo({ center: [2.33, 48.86] }); // centered on Paris if no emitter to display
        }
        let firstEmitter = Object.keys(this.props.emitters[keys[0]])[0]; // else, centered on the very first emitter received
        this.map.state.map.flyTo({ center: [this.props.emitters[keys[0]][firstEmitter].coordinates.lng, this.props.emitters[keys[0]][firstEmitter].coordinates.lat] });
    }


    /**
     * Returns the geometric center of all the points of the network, for simpler rendering
     * @param {String} network 
     */
    clusterCenter(network) {
        let x = 0;
        let y = 0;
        let stationLabels = Object.keys(this.state.emitters[network]);
        let N = stationLabels.length;
        for (let station_id of stationLabels) {
            let station = this.state.emitters[network][station_id];
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
     * When the pointer leaves, removes the highlight
     * @param {String} network 
     */
    mouseExit(network) {
        let highlights = JSON.parse(JSON.stringify(this.state.highlights));
        highlights[network] = 0;
        this.setState({ highlights: highlights });
    }

    /**
     * Gets the color of each network (white if null)
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
     * Toggles between the network names and their emitters numbers (triggered when clicking the "labels" button)
     */
    nameNetworks() {
        this.setState({ nameNets: !this.state.nameNets });
    }

    /**
     * Toggles the legend of the Map
     */
    toggle_legend() {
        this.setState({ legend: !this.state.legend });
    }

    render() {
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

                    <div id="legend" className="button is-grey">
                        <div id="showhide" >
                            {/* The checkboxes to hide/show everything */}
                            <div className="field">
                                <input className="is-checkradio is-block" type="checkbox" id="show_checkbox"
                                    name="show_checkbox" checked={this.props.showVal} onChange={this.props.changeShowVal} onClick={this.props.switchAll} />
                                <label htmlFor="show_checkbox">
                                    <span> </span>Show all
                            </label>
                            </div>
                            <div className="field">
                                <input className="is-checkradio is-block" type="checkbox" id="hide_checkbox" name="hide_checkbox" onClick={() => this.toggle_legend()} />
                                <label htmlFor="hide_checkbox">
                                    <span> </span>Legend
                            </label>
                            </div>
                        </div>
                        {
                            this.state.legend &&
                            <div className="legend">
                                <div className="legend-column">
                                    <div className="legend-item is-first">
                                        <p><img src={recImage} alt="Station symbol" />
                                            Recording station
                                        </p>
                                    </div>
                                    <div className="legend-item">
                                        <p><img src={centerImage} alt="Network centroid" />
                                            Network centroid
                                        </p>
                                    </div>
                                </div>
                                <div className="legend-column is-next">
                                    <div className="legend-item is-first">
                                        <p>
                                            <span className="legend-icon">
                                                <FontAwesomeIcon icon="circle" />
                                            </span>
                                            Emitter
                                        </p>
                                    </div>
                                    <div className="legend-item">
                                        <p>
                                            <span className="legend-icon">
                                                <FontAwesomeIcon icon="circle-notch" />
                                            </span>
                                            Lone emitter
                                        </p>
                                    </div>
                                </div>
                                <div className="legend-column is-next">
                                    <div className="legend-item is-first">
                                        <p><img src={lineImage} alt="Station symbol" />
                                            Link emitter to network
                                        </p>
                                    </div>
                                    <div className="legend-item">
                                        <p><img src={dashImage} alt="Network centroid" />
                                            Network correction suggestion
                                        </p>
                                    </div>
                                </div>
                            </div>
                        }




                    </div>
                    <Layer id="recStations" key="recStations" type="symbol" layout={{
                        "icon-image": "recStation",
                        "icon-size": 0.06
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
                            // network, Stations which contains all the actual emitters of the network and Lines which
                            // contains the connections between each node of the network.
                            // Those last 2 are rendered uniquely when toggled or if showAll is active.
                            let clusterCenter = this.clusterCenter(network); // the center coordinates
                            let color = this.getColor(network); // the color of the network
                            let emitters = this.state.emitters[network]; // al the emitters in this network
                            let emittersNumber = Object.keys(emitters).length;
                            let toggled = this.state.networksToggled[network];
                            toggled = !(toggled == undefined || !toggled);
                            toggled = toggled || this.props.showAll;
                            toggled = (emittersNumber == 1) || toggled;
                            // toggled is True if it's defined, not manually de-toggled (= False)
                            // or simply if showAll is active. Single emitters are always displayed.

                            let lines = toggled && (network != "-1000"); // We show the lines if the network is toggled.
                            // At the beginning, no line should be shown (the emitters are shown as a cloud of unconnected points).

                            let potentialLinks = []; // When using both ML and DL : list of all the corrected potential links given by the DL
                            Object.keys(emitters).map((track_id, keyy) => {
                                let potentialNetwork = emitters[track_id]["possible_network"];
                                if (potentialNetwork != undefined && potentialNetwork != network) { // If there was a match with another network...
                                    potentialLinks.push([[emitters[track_id]["coordinates"]["lng"], emitters[track_id]["coordinates"]["lat"]],
                                    this.clusterCenter(potentialNetwork)]); // ...the link between the emitters coordinates and the other network's center's coordiantes is saved.
                                }
                            });

                            let showPotential = (toggled && potentialLinks.length != 0); // We only
                            let textCenter = "" + emittersNumber;
                            if (this.state.nameNets) {
                                textCenter = "" + (parseInt(network) + 1);
                            }
                            return (
                                <div id={"cluster" + k} key={"cluster" + k}>
                                    {lines &&// conditionnal rendering
                                        <Lines
                                            clusterCenter={clusterCenter} color={color}
                                            network={network} stations={emitters} />
                                    }
                                    {network != "-1000" && emittersNumber > 1 && !toggled && // always rendering when simulation has started
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

                                    {network != "-1000" && emittersNumber > 1 && toggled && // always rendering when simulation has started
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
                                            stations={emitters} network={network}
                                            color={color} multiple={emittersNumber > 1}
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
                    <div className="widgets-colors">
                        <a id="colors-names-button" onClick={this.props.switchColorMap}>
                            <span className="icon">
                                <FontAwesomeIcon icon='palette' />
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
     * the emitters received from App.js, in the form :
     *   {    network_id : {
     *           emitter_id : {
     *               coordinates : {lat : float, lng : float}, ...
     *           }
     *       }
     *   }
     */
    emitters: PropTypes.objectOf(PropTypes.objectOf(PropTypes.object)).isRequired,
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
     * the function to toggle showAll
    */
    switchAll: PropTypes.func.isRequired,
    /**
     * the networks toggled/de-toggled manually by the user so far
     */
    networksToggled: PropTypes.objectOf(PropTypes.bool).isRequired

}


export default MapBox;

