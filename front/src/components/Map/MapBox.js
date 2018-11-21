import React, { Component } from "react";
import ReactMapboxGl, { Layer, Marker, Feature, ZoomControl, ScaleControl } from "react-mapbox-gl";
import colormap from "colormap";
import Stations from "./Stations.js";
import stationImage from "./satellite.png";
import Lines from "./Lines.js";
import { style } from "./style";
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
                offline: style
            },
            networksToggled: {
            }
        };
<<<<<<< HEAD
        for (let label of Object.keys(this.props.stations)) {
            this.state.networksToggled[label] = false;
        }
        this.toggleNetwork = this.toggleNetwork.bind(this);

=======
        this.componentWillReceiveProps = this.componentWillReceiveProps.bind(this);
>>>>>>> 94284f88c33ef95edbe9bb129e7a0acf49ae9392
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.stations !== this.props.stations) {
            this.setState({
                stations: nextProps.stations,
                networksLabels: Object.keys(nextProps.stations),
                colors: colormap({
                    colormap: 'jet',
                    nshades: Math.max(Object.keys(nextProps.stations).length, 8),
                    format: 'hex',
                    alpha: 1
                }) // once component received new props and has set its state, render component anew with new state.
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
<<<<<<< HEAD
        console.log(Map.get);
        let toggled = this.state.networksToggled[network];
        let networksToggledCopy = JSON.parse(JSON.stringify(this.state.networksToggled));
        networksToggledCopy[network] = !toggled;
        this.setState({ networksToggled: networksToggledCopy });
=======

>>>>>>> 94284f88c33ef95edbe9bb129e7a0acf49ae9392
    }

    render() {
        let colors = {}
        let i = 0;
        let image = new Image(512, 512);
        image.src = stationImage;
        let images = ["stationImage", image];
        for (let network of this.state.networksLabels) {
            colors[network] = this.state.colors[i];
            i += 1;
        }
        return (
            <div className="map-container">
                <Map
                    style={this.state.style[this.props.connection]}
                    containerStyle={{
                        height: "100%",
                        width: "100%",
                    }}

                >
                    <Layer
                        id="stations"
                        type="symbol"
                        layout={{
                            "icon-image": "stationImage",
                            "icon-size": 0.05
                        }}
                        images={images} >
                        {
                            Object.keys(this.props.recStations).map((station, k) =>
                                <Feature coordinates={[this.props.recStations[station].coordinates.lng, this.props.recStations[station].coordinates.lat]} key={100 * this.props.recStations[station].coordinates.lng + this.props.recStations[station].coordinates.lat}></Feature>
                            )
                        }
                    </Layer>                    {
                        this.state.networksLabels.map((network, k) => {
                            let clusterCenter = this.clusterCenter(network);
                            return (
<<<<<<< HEAD
                                <div id={"cluster" + k}>
                                    {this.state.networksToggled[network] &&
                                        <Lines
                                            clusterCenter={clusterCenter} color={colors[network]}
                                            network={network} stations={this.state.stations[network]} />
                                    }
=======
                                <div id={"cluster" + k} key={"cluster" + k}>
                                    <Lines
                                        clusterCenter={clusterCenter} color={colors[network]}
                                        network={network} stations={this.state.stations[network]} />
>>>>>>> 94284f88c33ef95edbe9bb129e7a0acf49ae9392
                                    <Layer
                                        id={"center" + network}
                                        type="circle"
                                        onClick={this.toggleNetwork(network)}
                                        paint={{
                                            "circle-color": colors[network],
                                            "circle-radius": 6
                                        }}>
                                        <Feature coordinates={clusterCenter} onClick={() => this.toggleNetwork(network)}></Feature>
                                    </Layer>
                                    {this.state.networksToggled[network] &&
                                        <Stations
                                            stations={this.state.stations[network]} network={network}
                                            color={this.state.colors[network]} />
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
/**
 * componentDidMount() {
        let map = new mapboxgl.Map({
            container: 'map',
            center: [8.3221, 46.5928],
            zoom: 1,
            style: style
        });
        map.addControl(new mapboxgl.Navigation());
    }
 */
export default MapBox;
