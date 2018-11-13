<<<<<<< HEAD
import React, { Component } from 'react';
import Websocket from 'react-websocket';

class SocketHandler extends Component {


  render() {
    return (
      <div>

        <Websocket url='ws://localhost:8000/startsimulation'
          onMessage={this.props.handleData} />
      </div>
    );
  }
}

export default SocketHandler;
=======
import React, {Component} from 'react';
import Websocket from 'react-websocket';
 
class SocketHandler extends Component {
 
 
    render() {
      return (
        <div>
 
          <Websocket url='ws://localhost:8000/startsimulation'
              onMessage={this.props.handleData}/>
        </div>
      );
    }
  }
 
  export default SocketHandler;
>>>>>>> 8d03b822a070dcbb5415a794595edd49c3caf5d7
