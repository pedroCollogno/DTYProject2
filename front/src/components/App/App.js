import React, { Component } from 'react';
import './App.css';
import MapBox from "../Map/MapBox";
import SocketHandler from "../Socket/SocketHandler";
import PostHandler from "../Http/PostHandler";

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
      emittors: {}, // list of all the detected stations so far
      stations: {},
      connection: 'offline',
      networksToggled: {
      }
    };
    this.newEmittor = this.newEmittor.bind(this);
    this.getStations = this.getStations.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.toggleNetwork = this.toggleNetwork.bind(this);
  }

  handleChange(event) {
    if (event.target.checked === true) {
      this.setState({ connection: 'online' })
    } else {
      this.setState({ connection: 'offline' })
    }
  }

  getConnection() {
    if (this.state.connection == "online") {
      return "offline";
    }
    return "online";
  }


  newEmittor(station) {
    if (station) {
      let stat = JSON.parse(station);
      if (stat.coordinates) {
        let dic = JSON.parse(JSON.stringify(this.state.emittors));
        if (dic["" + stat.network_id]) {
          dic["" + stat.network_id].push(stat);
        }
        else {
          dic["" + stat.network_id] = [stat];
        }
        this.setState({ emittors: dic, station: stat });
      }
    }
  }

  getStations(response) {
    this.setState({ stations: response.data });
    console.log(response.data);
  }

  toggleNetwork(network) {
    let networksToggledCopy = JSON.parse(JSON.stringify(this.state.networksToggled));
    if (networksToggledCopy[network] == undefined) {
      networksToggledCopy[network] = true;
    }
    else {
      networksToggledCopy[network] = !networksToggledCopy[network];
    }
    this.setState({ networksToggled: networksToggledCopy });
  }

  getBorderStyle(network) {
    if (this.state.networksToggled[network] == undefined || !this.state.networksToggled[network]) {
      return "none";
    }
    return "solid";
  }

  render() {
    return (
      <div className="App">
        <section className="hero is-primary is-bold" style={{ textAlign: 'left' }}>
          <div className="hero-body">
            <div className="container header">
              <div className="titles">
                <h1 className="title">
                  Thales Project
                </h1>
                <h2 className="subtitle">
                  AI demonstrator
                </h2>
              </div>

              <div className="field switch-container">
                <input id="switchRoundedOutlinedInfo" type="checkbox" name="switchRoundedOutlinedInfo" className="switch is-rtl is-rounded is-outlined is-info" onChange={this.handleChange} />
                <label htmlFor="switchRoundedOutlinedInfo"><strong>Switch to {this.getConnection()} map</strong></label>
              </div>
            </div>
          </div>
        </section>

        < SocketHandler handleData={this.newEmittor} />

        <div className="container">
          <MapBox stations={this.state.emittors} recStations={this.state.stations} connection={this.state.connection}
            toggleNetwork={this.toggleNetwork} />

          <PostHandler getStations={this.getStations} />
          {
            (Object.keys(this.state.emittors).length > 0 ?
              <div className="tile is-fullwidth" id="tabletile">
                <table className='table is-hoverable'>
                  <thead>
                    <tr>
                      <th>Emittor ID</th>
                      <th colSpan='2'>Coordinates</th>
                      <th>Frequency</th>
                      <th>Network</th>
                    </tr>
                  </thead>
                  {
                    Object.keys(this.state.emittors).map((key) => {
                      return (
                        <tbody key={key} style={{
                          borderStyle: this.getBorderStyle(key),
                          borderColor: "red",
                          borderWidth: 5
                        }}>
                          {
                            this.state.emittors[key].map((emittor) => {
                              return (
                                <tr key={emittor.track_id}>
                                  <td>{emittor.track_id}</td>
                                  <td>{emittor.coordinates.lat}</td>
                                  <td>{emittor.coordinates.lng}</td>
                                  <td>{emittor.frequency}</td>
                                  <td>{emittor.network_id + 1}</td>
                                </tr>
                              )
                            })
                          }
                          <tr></tr>
                        </tbody>
                      )
                    })
                  }
                </table>
              </div> : null)
          }
        </div>
      </div >
    );
  }
}



export default App;
