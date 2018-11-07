import React, { Component } from 'react';
import './App.css';
import WorldMap from "./WorldMap";
import {listenToServer} from "./api"

class App extends Component {
  stations = []; // list of all the detected stations so far
  constructor(props) {
    super(props);

    listenToServer((station) => { //connects to the server websocket and listens to events
      this.setState({ station });
      this.stations.push(station)
    });
  }

  state = {
    station : {reseau :"",place:"", id :""} // reseau : int, place : [lattitude, longitude]
  };


  render() {
    return (
      <div className="App">
        <p className="App-intro">
        Derniere station : {this.state.station.id}
        </p>
        <p>appartenant au réseau : {this.state.station.reseau}</p>
        <WorldMap stations={this.stations}/>
      </div>
    );
  }
}

export default App;
