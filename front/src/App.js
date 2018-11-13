import React, { Component } from 'react';
import './App.css';
import MapBox from "./MapBox";
import SocketHandler from "./SocketHandler";
import PostHandler from "./PostHandler";

// Set fontAwesome icons up -> Define all icons that will be used in the app.
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUpload, faDownload } from '@fortawesome/free-solid-svg-icons'

library.add(faUpload, faDownload)
// Setup complete

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
        <section class="hero is-primary is-bold" style={{ textAlign: 'left' }}>
          <div class="hero-body">
            <div class="container">
              <h1 class="title">
                Thales Project
              </h1>
              <h2 class="subtitle">
                AI demonstrator
              </h2>
            </div>
          </div>
        </section>
        < SocketHandler handleData={this.newEmittor} />

        <div className="container">
          <MapBox stations={this.state.stations} />
          <div className="tile is-fullwidth">
            <PostHandler getStations={this.getStations} />
            <table className='container table'>
              <tr>
                <th >Last station</th>
                <th colSpan='2'>Coordinates</th>
                <th>Network</th>
              </tr>
              <tr>
                <td>{this.state.station.track_id}</td>
                <td>{this.state.station.coordinates.lat}</td>
                <td>{this.state.station.coordinates.lng}</td>
                <td>{this.state.station.network_id}</td>
              </tr>
            </table>
          </div>


        </div>

      </div >
    );
  }
}



export default App;
