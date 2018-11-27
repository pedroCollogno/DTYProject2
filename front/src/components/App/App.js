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
      connection: "offline",
      networksToggled: {},
      showAll: false,
      hideAll: false
    };
    this.newEmittor = this.newEmittor.bind(this);
    this.getStations = this.getStations.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.toggleNetwork = this.toggleNetwork.bind(this);
    this.switchAll = this.switchAll.bind(this);

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


  newEmittor(emittor) {
    if (emittor) {
      let stat = JSON.parse(emittor);
      if (stat.coordinates) {
        let dic = JSON.parse(JSON.stringify(this.state.emittors));
        if (dic["" + stat.network_id]) {
          dic["" + stat.network_id][stat.track_id] = stat;
        }
        else {
          dic["" + stat.network_id] = {};
          dic["" + stat.network_id][stat.track_id] = stat;
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
    console.log(networksToggledCopy);
    if (networksToggledCopy[network] == undefined) {
      networksToggledCopy[network] = true;
    }
    else {
      networksToggledCopy[network] = !networksToggledCopy[network];
    }
    this.setState({ networksToggled: networksToggledCopy });
  }

  getBorderStyle(network) {
    let toggled = this.state.networksToggled[network];
    toggled = !(toggled == undefined || !toggled);
    if (!this.state.hideAll && (toggled || this.state.showAll)) {
      return "solid";
    }
    return "none";
  }

  switchAll(all) {
    if (all) {
      this.setState({
        showAll: !this.state.showAll
      });
    }
    else {
      this.setState({
        hideAll: !this.state.hideAll
      });
    }
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
          <MapBox emittors={this.state.emittors} recStations={this.state.stations} connection={this.state.connection}
            toggleNetwork={this.toggleNetwork} switchAll={this.switchAll}
            hideAll={this.state.hideAll} showAll={this.state.showAll} networksToggled={this.state.networksToggled} />

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
                            Object.keys(this.state.emittors[key]).map((emittor_id) => {
                              return (
                                <tr key={this.state.emittors[key][emittor_id].track_id}>
                                  <td>{this.state.emittors[key][emittor_id].track_id}</td>
                                  <td>{this.state.emittors[key][emittor_id].coordinates.lat}</td>
                                  <td>{this.state.emittors[key][emittor_id].coordinates.lng}</td>
                                  <td>{this.state.emittors[key][emittor_id].frequency}</td>
                                  <td>{this.state.emittors[key][emittor_id].network_id + 1}</td>
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
