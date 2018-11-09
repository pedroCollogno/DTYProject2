import React, {Component} from 'react';
import Websocket from 'react-websocket';
 
class SocketHandler extends Component {
 
 
    render() {
      return (
        <div>
 
          <Websocket url='ws://localhost:8000/test'
              onMessage={this.props.handleData}/>
        </div>
      );
    }
  }
 
  export default SocketHandler;