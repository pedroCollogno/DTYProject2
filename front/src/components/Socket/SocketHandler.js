import React, { Component } from 'react';
import Websocket from 'react-websocket';
import PropTypes from "prop-types";

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

SocketHandler.propTypes = {
  /**
   * the function to call when receiving a message.
   * Expects an emittor, in the form of a stringified JSON
   */
  handleData: PropTypes.func.isRequired
}

export default SocketHandler;
