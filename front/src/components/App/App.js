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
      emittors: {}, // list of all the detected stations so far in the form :
      // { network_id : 
      //        { track_id : {coordinates: { lat: int, lng: int }, ... }
      // }
      stations: {}, // list of the reception stations
      connection: "offline", // selcects the style of the map (to be fetched from the Web or locally)
      networksToggled: {}, // the networks toggled : used to highlight them in the list and display them on the map
      showAll: false, // the state of the checkbuttons of the map (combined with networksToggled)
      hideAll: false
    };
    this.newEmittor = this.newEmittor.bind(this); // functions that are allowed to update the state of the component
    this.newEmittors = this.newEmittors.bind(this);
    this.getStations = this.getStations.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.toggleNetwork = this.toggleNetwork.bind(this);
    this.switchAll = this.switchAll.bind(this);
    this.reset = this.reset.bind(this);

  }


  /**
   * Toggles between "online" and "offline" display
   * @param {*} event 
   */
  handleChange(event) {
    if (event.target.checked === true) {
      this.setState({ connection: 'online' })
    } else {
      this.setState({ connection: 'offline' })
    }
  }


  /**
   * Returns the text to be displayed depending on the connection
   * i.e. : "Switch to online connection" if the state connection is currently offline
   */
  getConnection() {
    if (this.state.connection == "online") {
      return "offline";
    }
    return "online";
  }

  /**
   * Adds the emittor coming from the backend to the list of the emittors.
   * Stores it as {network_id : {track_id : {coordinates : {lat : int, lng : int}, ...}}}
   * @param {*} emittor 
   */
  newEmittor(emittor) {
    if (emittor) {
      let stat = JSON.parse(emittor);
      if (stat.coordinates) {
        let longitude = stat.coordinates.lng;
        if (longitude < -180) {
          stat.coordinates.lng = longitude + 360;
        }
        let dic = JSON.parse(JSON.stringify(this.state.emittors));
        if (dic["" + stat.network_id]) {
          dic["" + stat.network_id][stat.track_id] = stat;
        }
        else {
          dic["" + stat.network_id] = {};
          dic["" + stat.network_id][stat.track_id] = stat;
        }
        this.setState({ emittors: dic });
      }
    }
  }

  newEmittors(emittors) {
    if (emittors) {
      let stats = JSON.parse(emittors);
      let dic = JSON.parse(JSON.stringify(this.state.emittors));
      if (Object.entries(stats)[0][1]["network_id"] != undefined) {
        for (let key of Object.keys(stats)) {
          let stat = stats[key];
          if (stat.coordinates) {
            let longitude = stat.coordinates.lng;
            if (longitude < -180) {
              stat.coordinates.lng = longitude + 360;
            }
            if (dic["" + stat.network_id]) {
              dic["" + stat.network_id][stat.track_id] = stat;
            }
            else {
              dic["" + stat.network_id] = {};
              dic["" + stat.network_id][stat.track_id] = stat;
            }
          }
        }
        this.setState({ emittors: dic });
      }

    }
  }

  /**
   * Adds the reception stations sent from the backend (all at once) to the state of the component.
   * Stations are expected to be : {data : {station1 : {coordinates : {lat : int, lng : int}}},
   *                                       {station2 : {coordinates : {lat : int, lng : int}}}, ...
   *                                }
   * @param {*} response 
   */
  getStations(response) {
    this.setState({ stations: response.data });
    console.log(response.data);
  }

  /**
   * Updates the state of the component (and thus the rendering) whenever a network is manually toggled
   * @param {*} network 
   */
  toggleNetwork(network) {
    if (network == null) {
      console.log("Network is null");
    }
    else {
      let networksToggledCopy = JSON.parse(JSON.stringify(this.state.networksToggled));
      if (networksToggledCopy[network] == undefined) {
        networksToggledCopy[network] = true;
      }
      else {
        networksToggledCopy[network] = !networksToggledCopy[network];
      }
      this.setState({ networksToggled: networksToggledCopy });
    }

  }

  /**
   * Gets the display mode (highlighted or not) of the given network in the rendered list
   * @param {*} network 
   */
  getBorderStyle(network) {
    let toggled = this.state.networksToggled[network];
    toggled = !(toggled == undefined || !toggled);
    if (!this.state.hideAll && (toggled || this.state.showAll)) {
      return "solid";
    }
    return "none";
  }

  /**
   * Called by pressing the showAll or hideAll buttons. Updates the state accordingly.
   * The param "all" is a boolean : True if showAll was pressed, False if hideAll was pressed.
   * @param {*} all 
   */
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

  reset() {
    console.log("Reset");
    this.setState({
      emittors: {}, // list of all the detected stations so far in the form :
      // { network_id : 
      //        { track_id : {coordinates: { lat: int, lng: int }, ... }
      // }
      stations: {}, // list of the reception stations
      connection: "offline", // selcects the style of the map (to be fetched from the Web or locally)
      networksToggled: {}, // the networks toggled : used to highlight them in the list and display them on the map
      showAll: false, // the state of the checkbuttons of the map (combined with networksToggled)
      hideAll: false
    });
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

        {/* Handles the HandShaking and sends a "begin" message to the backend Socket */}
        < SocketHandler handleData={this.newEmittors} />

        <div className="container">
          {/* Handles the displays on a canvas */}
          <MapBox emittors={this.state.emittors} recStations={this.state.stations} connection={this.state.connection}
            toggleNetwork={this.toggleNetwork} switchAll={this.switchAll}
            hideAll={this.state.hideAll} showAll={this.state.showAll} networksToggled={this.state.networksToggled} />

          {/* Handles the HTTP requests and their responses from the backend */}
          <PostHandler getStations={this.getStations} reset={this.reset} />
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
