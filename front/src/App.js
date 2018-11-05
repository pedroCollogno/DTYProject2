import React, { Component } from 'react';
import './App.css';
import WorldMap from "./WorldMap";

class App extends Component {
  stations = [];
  constructor(props) {
    super(props);

    listenToServer((station) => { //connects to the server websocket
      this.setState({ station });
      this.stations.push(station)
    });
  }

  state = {
    station : {reseau :"",place:"", id :""}
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
