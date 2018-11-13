import React, { Component } from 'react';
import './App.css';
import MapBox from "./MapBox";
import SocketHandler from "./SocketHandler";
import PostHandler from "./PostHandler";

class App extends Component {
  constructor() {
    super();
    this.state = {
      station: { network_id: 0, coordinates: { lat: 0, lng: 0 }, track_id: 0 },
      stations: {} // list of all the detected stations so far
    };
    this.newEmittor = this.newEmittor.bind(this);
  }


  newEmittor(station) {
    if (station) {
      let stat = JSON.parse(station);
      if (stat.coordinates) {
        let dic = JSON.parse(JSON.stringify(this.state.stations));
        if (dic["" + stat.network_id]) {
          dic["" + stat.network_id].push(stat);
        }
        else {
          dic["" + stat.network_id] = [stat];
        }
        this.setState({ stations: dic, station: stat });
      }
    }
  }

  getStations(response) {
    console.log(response.data);
  }


  render() {
    return (
      <div className="App">
        < SocketHandler handleData={this.newEmittor} />
        < MapBox stations={this.state.stations} />
        <h1 style={{ fontFamily: "Impact" }}>Thales Project</h1>
        <p>Last station : {this.state.station.track_id}</p>
        <p>Coordinates : {this.state.station.coordinates.lat}, {this.state.station.coordinates.lng}</p>
        <p>Network : {this.state.station.network_id}</p>
        < PostHandler getStations={this.getStations} />
      </div>
    );
  }
}

export default App;
