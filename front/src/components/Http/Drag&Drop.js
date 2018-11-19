import React, { Component } from 'react';
import FileDrop from 'react-file-drop';
import './Drag&Drop.css';


class DropZone extends Component {


  render() {
    return (
      <FileDrop onDrop={this.props.handleDrop}>
        {this.props.text}
      </FileDrop>
    )

  }
}

export default DropZone;