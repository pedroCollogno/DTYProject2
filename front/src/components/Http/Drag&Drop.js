import React, { Component } from 'react';
import FileDrop from 'react-file-drop';
import './Drag&Drop.css';


const styles = { border: '1px solid black', width: 600, color: 'black', padding: 20 };
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