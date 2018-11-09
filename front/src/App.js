import React, { Component } from 'react';
import './App.css';
import MapBox from "./MapBox";
import SocketHandler from "./SocketHandler";

class App extends Component {
  constructor() {
    super();
    this.state = {
      station : {reseau :0,place:[0, 0], id :0},
      stations : [{reseau :0,place:[2, 45], id :0}] // list of all the detected stations so far
    };
    this.newStation = this.newStation.bind(this);
  }


  newStation(station) {
    let array = this.state.stations.splice(0);
    array.push(JSON.parse(station));
    let stat = JSON.parse(JSON.stringify(station))
    this.setState({stations : array, station : stat});
    console.log(this.state.stations);
  }


  render() {
    return (
      <div className="App">
        < SocketHandler handleData={this.newStation}/>
        < MapBox stations={this.state.stations} lastStation={this.state.station}/>
        <h1 style = {{fontFamily:"Impact"}}>Thales Project</h1>
      </div>
    );
  }
}

export default App;
