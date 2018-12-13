import React, { Component } from 'react';
import './App.css';
import MapBox from "../Map/MapBox";
import SocketHandler from "../Socket/SocketHandler";
import PostHandler from "../Http/PostHandler";
import colormap from "colormap";
import Dashboard from '../Modal/Dashboard';
import thales_logo from './thales_logo.png'

// Set fontAwesome icons up -> Define all icons that will be used in the app.
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUpload, faDownload, faUndo, faPalette, faPlay, faPause, faStop, faLocationArrow, faCheck, faExclamationTriangle, faCircle, faCircleNotch, faTags, faInfo, faMagic } from '@fortawesome/free-solid-svg-icons'
library.add(faUpload, faDownload, faUndo, faPalette, faPlay, faPause, faStop, faLocationArrow, faCheck, faExclamationTriangle, faCircle, faCircleNotch, faTags, faInfo, faMagic)
// Setup complete, import them
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'


const colorMapNames = ["jet", "hsv", "rainbow", "rainbow-soft"];
const colorMapMins = [7, 12, 10, 12];
const colorMapNumber = colorMapNames.length;

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

/**
 * Displays an emittor's important characteristics in the table (returns an HTML "row");
 * @param {*} emittor 
 */
function show_network(emittor) {
  let network = emittor.network_id
  let icon = "check"
  let possible_network = -1000
  if (Object.keys(emittor).includes('possible_network')) {
    possible_network = emittor.possible_network
    if (possible_network != network) { // Displays an exclamation triangle if the likeliest network is not the DBScan one
      icon = "exclamation-triangle"
    }
  }
  return (
    <span className="network-display">
      <p>{network + 1}</p> <FontAwesomeIcon icon={icon} className={icon}></FontAwesomeIcon>
    </span>
  )
}

/**
 * Returns an icon indicating the state of the emittor (emitting/silent).
 * @param {*} emittor 
 */
function show_talking(emittor) {
  let icon = "circle";
  let clss = "not-talking";
  let talking = false
  if (Object.keys(emittor).includes('talking')) {
    talking = emittor.talking
    if (talking) {
      clss = "talking"
    }
  }
  return (
    <FontAwesomeIcon icon={icon} className={clss}></FontAwesomeIcon>
  )
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
      cycle_mem_info: {}, // 
      global_mem_info: {}, // 
      connection: "offline", // selcects the style of the map (to be fetched from the Web or locally)
      networksToggled: {}, // the networks toggled : used to highlight them in the list and display them on the map
      showAll: false, // the state of the checkbuttons of the map (combined with networksToggled)
      hideAll: false,
      hideVal: false,
      showVal: false,
      white: "",
      simulationMode: "",
      colors: colormap({ // a colormap to set a different color for each network
        colormap: "jet",
        nshades: 7 // 7 is the minimum number of colors for "jet"
      }),
      colorMapType: 0
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
    this.hoverIn = this.hoverIn.bind(this);
    this.hoverOut = this.hoverOut.bind(this);
    this.changeSimulationMode = this.changeSimulationMode.bind(this);
    this.switchColorMap = this.switchColorMap.bind(this);
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
   * Gets all emittors positions after the prps upload. Displays them without prediction on their networks.
   * @param {*} response 
   */
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
   * @param {*} data 
   */
  newEmittors(data) {
    if (data) {
      let colorMin = colorMapMins[this.state.colorMapType]; // the minimum number of colors
      let d = JSON.parse(data);
      let dic = JSON.parse(JSON.stringify(this.state.emittors));
      if (dic["-1000"] != undefined) {
        delete dic["-1000"];
      }
      if (Object.entries(d)) {
        if (Object.entries(d)[0]) {
          if (Object.entries(d)[0][1]["network_id"] != undefined) {
            for (let key of Object.keys(d)) {
              let emit = d[key];
              if (emit.coordinates) {
                let longitude = emit.coordinates.lng;
                if (longitude < -180) {
                  emit.coordinates.lng = longitude + 360;
                }
                if (dic["" + emit.network_id] && dic["" + emit.network_id][emit.track_id] == undefined) {
                  let id = "" + (emit.network_id + 1) + "_" + (Object.keys(dic["" + emit.network_id]).length + 1);
                  dic["" + emit.network_id][emit.track_id] = emit;
                  dic["" + emit.network_id][emit.track_id]["id"] = id;

                }
                else {
                  dic["" + emit.network_id] = {};
                  dic["" + emit.network_id][emit.track_id] = emit;
                  dic["" + emit.network_id][emit.track_id]["id"] = "" + (emit.network_id + 1) + "_1";
                }
              }
            }

            let colorMap = colormap({
              colormap: colorMapNames[this.state.colorMapType],
              nshades: Math.max(Object.keys(dic).length, colorMin),
              alpha: 1
            });
            this.setState({ emittors: dic, colors: colorMap });

          } else if (Object.keys(d)[0].includes("cycle_mem_info")) {
            this.setState({ cycle_mem_info: d[Object.keys(d)[0]] });
          } else if (Object.keys(d)[0].includes("global_mem_info")) {
            this.setState({ global_mem_info: d[Object.keys(d)[0]] });
          }
        }
      }
    }
  }

  switchColorMap() {
    let index = this.state.colorMapType;
    index += 1;
    if (index > colorMapNumber) {
      index -= colorMapNumber;
    }
    let colormapName = colorMapNames[index];
    let colorMin = colorMapMins[index]; // the minimum number of colors
    let totalNetworksNumber = Object.keys(this.state.emittors).length;
    let colorMap = colormap({
      colormap: colormapName,
      nshades: Math.max(totalNetworksNumber, colorMin),
      alpha: 1 // opacity
    });
    this.setState({
      colors: colorMap,
      colorMapType: index
    });
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
   * @param {String} network 
   */
  toggleNetwork(network) {
    if (network == null) {
      console.log("Network is null");
    }
    else {
      let networksToggledCopy = JSON.parse(JSON.stringify(this.state.networksToggled));
      networksToggledCopy[network] = !networksToggledCopy[network];
      this.setState({ networksToggled: networksToggledCopy });
    }

  }

  /**
   * Gets the display mode (highlighted or not) of the given network in the rendered list
   * @param {String} network 
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
   * @param {String} network 
   */
  getBorderColor(network) {
    let networkNumber = parseInt(network);
    if (networkNumber < 0) {
      return "#5c5c5c";
    }
    return this.state.colors[networkNumber];
  }

  /**
   * Called by pressing the showAll or hideAll buttons. Updates the state accordingly.
   * The param "all" is a boolean : True if showAll was pressed, False if hideAll was pressed.
   * @param {Boolean} all 
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

  /**
   * Resets the state of the component (called by pressing the "reset" button in the PostHandler component)
   */
  reset() {
    console.log("Resetting App.js.");
    this.setState({
      emittors: {},
      stations: {},
      cycle_mem_info: {},
      global_mem_info: {},
      connection: "offline",
      networksToggled: {},
      showAll: false,
      hideAll: false,
      hideVal: false,
      showVal: false,
      white: "",
      colors: colormap({ // a colormap to set a different color for each network
        colormap: "jet",
        nshades: 7 // 7 is the minimum number of colors for "jet"
      }),
      colorMapType: 0
    });
  }

  /**
   * Changes the "show all" checkbox value (in the MapBox component)
   */
  changeShowVal() {
    this.setState({ showVal: !this.state.showVal });
  }



  /**
 * Changes the "hide all" checkbox value (in the MapBox component)
 */
  changeHideVal() {
    this.setState({ hideVal: !this.state.hideVal });
  }

  /**
   * Highlights (in white) the emittor corresponding to the row hovered over by the mouse if its network is toggled
   * @param {String} network 
   * @param {*} emittor 
   */
  hoverIn(network, emittor) {
    if (this.state.networksToggled[network] == true) {
      this.setState({ white: emittor });
    }
  }

  /**
   * Removes the highlighting (white) effect (if there was any) when the mouse leaves the row.
   * @param {*} emittor 
   */
  hoverOut(emittor) {
    if (this.state.white == emittor) {
      this.setState({ white: "" });
    }
  }

  /**
   * Updates the displayed simulation mode.
   * @param {String} simulMode 
   */
  changeSimulationMode(simulMode) {
    this.setState({ simulationMode: simulMode });
  }

  render() {
    return (
      <div className="App">
        <section className="hero is-primary is-bold is-small" style={{ textAlign: 'left' }}>
          <div className="hero-body">
            <div className="container header">
              <div className="titles">
                <h1 className="title">
                  <img src={thales_logo} height="45" width="200" alt="Thales Logo"></img>
                </h1>
                <h2 className="subtitle">
                  AI demonstrator
                </h2>

                <h2 className="subtitle">
                  {this.state.simulationMode}
                </h2>

              </div>
              <div className="field switch-container">
                <input id="switchRoundedOutlinedInfo" type="checkbox" name="switchRoundedOutlinedInfo" className="switch is-rtl is-rounded is-outlined is-info" onChange={this.handleChange} />
                <label htmlFor="switchRoundedOutlinedInfo"><strong>Switch to {this.getConnection()} map</strong></label>
                <Dashboard emittors={this.state.emittors} cycle_mem_info={this.state.cycle_mem_info} global_mem_info={this.state.global_mem_info} simulationMode={this.state.simulationMode} />
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
            changeHideVal={this.changeHideVal} changeShowVal={this.changeShowVal} hideVal={this.state.hideVal} showVal={this.state.showVal}
            white={this.state.white} colors={this.state.colors} switchColorMap={this.switchColorMap} />
          {
            <div id="tabletile">
              <table className='table is-hoverable'>
                <thead>
                  <tr>
                    <th>ID</th>
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
                      let emittors = this.state.emittors[key];
                      return (
                        <tbody key={key} style={{
                          borderStyle: this.getBorderStyle(key),
                          borderColor: this.getBorderColor(key),
                          borderWidth: 5
                        }}>
                          {
                            Object.keys(emittors).map((emittor_id) => {
                              let emittor = emittors[emittor_id];
                              return (
                                <tr key={emittor.track_id} onClick={() => this.toggleNetwork(key)} onMouseEnter={() => this.hoverIn(key, emittor_id)}
                                  onMouseLeave={() => this.hoverOut(emittor_id)}>
                                  <td>{emittor.id}</td>
                                  <td>{int_to_emittor_type(emittor.emission_type)}</td>
                                  <td>{deg_to_dms(emittor.coordinates.lat)}</td>
                                  <td>{deg_to_dms(emittor.coordinates.lng)}</td>
                                  <td>{round_frequency(emittor.frequency)} MHz</td>
                                  <td>{show_network(emittor)}</td>
                                  <td>{show_talking(emittor)}</td>
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
                    let emittors = this.state.emittors[key];
                    return (
                      <tbody key={key} style={{
                        borderStyle: this.getBorderStyle(key),
                        borderColor: this.getBorderColor(key),
                        borderWidth: 5
                      }}>
                        {
                          Object.keys(emittors).map((emittor_id) => {
                            let emittor = emittors[emittor_id];
                            return (
                              <tr key={this.state.emittors[key][emittor_id].track_id} onClick={() => this.toggleNetwork(key)} onMouseEnter={() => this.hoverIn(key, emittor_id)}
                                onMouseLeave={() => this.hoverOut(emittor_id)}>
                                <td>{emittor.id}</td>
                                <td>{int_to_emittor_type(emittor.emission_type)}</td>
                                <td>{deg_to_dms(emittor.coordinates.lat)}</td>
                                <td>{deg_to_dms(emittor.coordinates.lng)}</td>
                                <td>{round_frequency(emittor.frequency)} MHz</td>
                                <td>{show_network(emittor)}</td>
                                <td>{show_talking(emittor)}</td>
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
            </div>
          }
        </div>

        {/* Handles the HTTP requests and their responses from the backend */}
        <PostHandler getStations={this.getStations} reset={this.reset} changeSimulationMode={this.changeSimulationMode}
          getEmittorsPositions={this.getEmittorsPositions} cycle_mem_info={this.state.cycle_mem_info} network_num={Object.keys(this.state.emittors).length} />

      </div >
    );
  }
}



export default App;
