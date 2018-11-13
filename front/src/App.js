import React, { Component } from 'react';
import './App.css';
import MapBox from "./MapBox";
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
        <section class="hero is-primary" style={{ textAlign: 'left' }}>
          <div class="hero-body">
            <div class="container">
              <h1 class="title">
                Thales project
              </h1>
              <h2 class="subtitle">
                AI demonstrator
              </h2>
            </div>
          </div>
        </section>

        <div className='container'>
          < MapBox stations={this.state.stations} lastStation={this.state.station} />
        </div>
        <p>Last station : {this.state.station.track_id}</p>
        <p>Coordinates : {this.state.station.coordinates.lat}, {this.state.station.coordinates.lng}</p>
        <p>Network : {this.state.station.network_id}</p>
      </div >
    );
  }
}

export default App;
