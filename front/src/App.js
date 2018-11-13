import React, { Component } from 'react';
import './App.css';
import OfflineMap from "./OfflineMap";
import SocketHandler from "./SocketHandler";

class App extends Component {
  constructor() {
    super();
    this.state = {
      station: { network_id: 0, coordinates: { lat: 0, lng: 0 }, track_id: 0 },
      stations: [] // list of all the detected stations so far
    };
    this.newStation = this.newStation.bind(this);
  }


  newStation(station) {
    if (station) {
      let stat = JSON.parse(station);
      if (this.state.stations.length < 60 && stat.coordinates) {
        let array = this.state.stations.slice();
        array.push(stat);
        console.log(array);
        this.setState({ stations: array, station: stat });
      }
    }
  }


  render() {
    return (
      <div className="App">
        < SocketHandler handleData={this.newStation} />
        <OfflineMap></OfflineMap>
        <h1 style={{ fontFamily: "Impact" }}>Thales Project</h1>
        <p>Last station : {this.state.station.track_id}</p>
        <p>Coordinates : {this.state.station.coordinates.lat}, {this.state.station.coordinates.lng}</p>
        <p>Network : {this.state.station.network_id}</p>
      </div>
    );
  }
}

export default App;
