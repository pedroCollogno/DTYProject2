import React, { Component } from 'react';
import './App.css';
import MapBox from "../Map/MapBox";
import SocketHandler from "../Socket/SocketHandler";
import PostHandler from "../Http/PostHandler";
import colormap from "colormap";
import Dashboard from '../Modal/Dashboard'

// Set fontAwesome icons up -> Define all icons that will be used in the app.
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUpload, faDownload, faUndo, faPlay, faPause, faLocationArrow } from '@fortawesome/free-solid-svg-icons'

library.add(faUpload, faDownload, faUndo, faPlay, faPause, faLocationArrow)
// Setup complete

function deg_to_dms(deg) {
  let d = Math.floor(deg);
  let minfloat = (deg - d) * 60;
  let m = Math.floor(minfloat);
  let secfloat = (minfloat - m) * 60;
  let s = Math.round(secfloat);
  // After rounding, the seconds might become 60. These two
  // if-tests are not necessary if no rounding is done.
  if (s == 60) {
    m++;
    s = 0;
  }
  if (m == 60) {
    d++;
    m = 0;
  }
  return ("" + d + "°" + m + "'" + s + '"');
}

/**
 * Gives you the emittor type as a string from an integer input
 * @param {int} type 
 */
function int_to_emittor_type(type) {
  if (type) {
    const new_type = parseInt(type)

    switch (new_type) {
      case 1:
        return "FF";
      case 2:
        return "EVF";
      case 3:
        return "BURST";
      default:
        return "?";
    }
  }
}

/**
 * Rounds the given frequency to MHz
 * @param {float} freq 
 */
function round_frequency(freq) {
  let MHz = Math.floor(freq / 10000) / 100
  return MHz
}
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
      hideAll: false,
      hideVal: false,
      showVal: false,
      total_duration: 0,
      progress: 0,
      white: ""
    };
    // functions that are allowed to update the state of the component
    this.newEmittors = this.newEmittors.bind(this);
    this.getStations = this.getStations.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.toggleNetwork = this.toggleNetwork.bind(this);
    this.switchAll = this.switchAll.bind(this);
    this.getEmittorsPositions = this.getEmittorsPositions.bind(this);
    this.reset = this.reset.bind(this);
    this.changeShowVal = this.changeShowVal.bind(this);
    this.changeHideVal = this.changeHideVal.bind(this);
    this.clickRow = this.clickRow.bind(this);
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

  getEmittorsPositions(response) {
    let dic = {};
    let data = response.data;
    let undefinedNetwork = data[Object.keys(data)[0]]["network_id"];
    for (let track_id of Object.keys(data)) {
      let emittor = data[track_id];
      if (emittor.coordinates != null) {
        dic[track_id] = emittor;
      }
    }
    let newEmittors = {};
    newEmittors[undefinedNetwork] = dic;
    this.setState({ emittors: newEmittors });
  }

  /**
   * Adds the emittors coming from the backend to the list of the emittors.
   * Stores them as {network_id : {track_id : {coordinates : {lat : int, lng : int}, ...}}}
   * @param {*} emittors 
   */
  newEmittors(emittors) {
    if (emittors) {
      let emitts = JSON.parse(emittors);
      let dic = JSON.parse(JSON.stringify(this.state.emittors));
      let total_duration = 0;
      let progress = 0;
      if (dic["-1000"] != undefined) {
        delete dic["-1000"];
      }
      if (Object.entries(emitts)[0][1]["network_id"] != undefined) {
        for (let key of Object.keys(emitts)) {
          let emit = emitts[key];
          if (emit.coordinates) {
            let longitude = emit.coordinates.lng;
            if (longitude < -180) {
              emit.coordinates.lng = longitude + 360;
            }
            if (dic["" + emit.network_id]) {
              dic["" + emit.network_id][emit.track_id] = emit;
            }
            else {
              dic["" + emit.network_id] = {};
              dic["" + emit.network_id][emit.track_id] = emit;
            }

            total_duration = emit.total_duration;

            if (progress == 0) {
              progress = emit.progress;
            }
          }
        }
        this.setState({ emittors: dic, progress: progress, total_duration: total_duration });
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
   * Gets the display color of the given network in the rendered list
   * @param {*} network 
   */
  getBorderColor(network) {
    let colors = colormap({ // a colormap to set a different color for each network
      colormap: 'jet',
      nshades: Math.max(Object.keys(this.state.emittors).length, 8), // 8 is the minimum number of colors
      format: 'hex',
      alpha: 1 // opacity
    })
    return colors[network]
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
    console.log("Resetting App.js.");
    this.setState({
      emittors: {}, // list of all the detected stations so far in the form :
      // { network_id : 
      //        { track_id : {coordinates: { lat: int, lng: int }, ... }
      // }
      stations: {}, // list of the reception stations
      connection: "offline", // selcects the style of the map (to be fetched from the Web or locally)
      networksToggled: {}, // the networks toggled : used to highlight them in the list and display them on the map
      showAll: false, // the state of the checkbuttons of the map (combined with networksToggled)
      hideAll: false,
      hideVal: false,
      showVal: false,
      total_duration: 0,
      progress: 0,
      white: ""
    });
  }

  changeShowVal() {
    this.setState({ showVal: !this.state.showVal });
  }

  changeHideVal() {
    this.setState({ hideVal: !this.state.hideVal });
  }

  clickRow(network, emittor) {
    this.setState({ white: emittor });
    this.toggleNetwork(network);
  }

  getBackgroundStyle(emittor) {
    if (this.state.white == emittor) {
      return ({ borderWidth: 10 });
    }
    return ({ borderWidth: 0 });
  }

  render() {
    return (
      <div className="App">
        <section className="hero is-primary is-bold is-small" style={{ textAlign: 'left' }}>
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
                <Dashboard emittors={this.state.emittors}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Handles the HandShaking and sends a "begin" message to the backend Socket */}
        < SocketHandler handleData={this.newEmittors} />

        <div className="map-table-container">
          {/* Handles the displays on a canvas */}
          <MapBox emittors={this.state.emittors} recStations={this.state.stations} connection={this.state.connection}
            toggleNetwork={this.toggleNetwork} switchAll={this.switchAll}
            hideAll={this.state.hideAll} showAll={this.state.showAll} networksToggled={this.state.networksToggled}
            changeHideVal={this.changeHideVal} changeShowVal={this.changeShowVal} hideVal={this.state.hideVal} showVal={this.state.showVal} />
          {
            <div className="test" id="tabletile">
              <table className='table is-hoverable'>
                <thead>
                  <tr>
                    <th>Type</th>
                    <th colSpan='2'>Coordinates</th>
                    <th>Frequency</th>
                    <th>Network</th>
                    <th>Just talked</th>
                  </tr>
                </thead>
                {
                  Object.keys(this.state.emittors).map((key) => {
                    if (this.state.networksToggled[key]) {
                      return (
                        <tbody key={key} style={{
                          borderStyle: this.getBorderStyle(key),
                          borderColor: this.getBorderColor(key),
                          borderWidth: 5
                        }}>
                          {
                            Object.keys(this.state.emittors[key]).map((emittor_id) => {
                              return (
                                <tr key={this.state.emittors[key][emittor_id].track_id} onClick={() => this.clickRow(key, emittor_id)} style={this.getBackgroundStyle(emittor_id)}>
                                  <td>{int_to_emittor_type(this.state.emittors[key][emittor_id].emission_type)}</td>
                                  <td>{deg_to_dms(this.state.emittors[key][emittor_id].coordinates.lat)}</td>
                                  <td>{deg_to_dms(this.state.emittors[key][emittor_id].coordinates.lng)}</td>
                                  <td>{round_frequency(this.state.emittors[key][emittor_id].frequency)} MHz</td>
                                  <td>{this.state.emittors[key][emittor_id].network_id + 1}</td>
                                  <td>{"" + this.state.emittors[key][emittor_id].talking}</td>
                                </tr>
                              )
                            })
                          }
                          <tr></tr>
                        </tbody>
                      )
                    }
                  })
                }
                {
                  Object.keys(this.state.emittors).map((key) => {
                    if (!this.state.networksToggled[key]) {
                      return (
                        <tbody key={key} style={{
                          borderStyle: this.getBorderStyle(key),
                          borderColor: this.getBorderColor(key),
                          borderWidth: 5
                        }}>
                          {
                            Object.keys(this.state.emittors[key]).map((emittor_id) => {
                              return (
                                <tr key={this.state.emittors[key][emittor_id].track_id} onClick={() => this.clickRow(key, emittor_id)} style={this.getBackgroundStyle(emittor_id)}>
                                  <td>{int_to_emittor_type(this.state.emittors[key][emittor_id].emission_type)}</td>
                                  <td>{deg_to_dms(this.state.emittors[key][emittor_id].coordinates.lat)}</td>
                                  <td>{deg_to_dms(this.state.emittors[key][emittor_id].coordinates.lng)}</td>
                                  <td>{round_frequency(this.state.emittors[key][emittor_id].frequency)} MHz</td>
                                  <td>{this.state.emittors[key][emittor_id].network_id + 1}</td>
                                  <td>{"" + this.state.emittors[key][emittor_id].talking}</td>
                                </tr>
                              )
                            })
                          }
                          <tr></tr>
                        </tbody>
                      )
                    }
                  })
                }
              </table>
            </div>
          }
        </div>

        {/* Handles the HTTP requests and their responses from the backend */}
        <PostHandler getStations={this.getStations} reset={this.reset} getEmittorsPositions={this.getEmittorsPositions} total_duration={this.state.total_duration} progress={this.state.progress} />

      </div >
    );
  }
}



export default App;
