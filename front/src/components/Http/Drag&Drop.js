import React, { Component } from 'react';
import FileDrop from 'react-file-drop';
import './Drag&Drop.css';
import PropTypes from "prop-types";


class DropZone extends Component {


  render() {
    return (
      <FileDrop onDrop={this.props.handleDrop}>
        {this.props.text}
      </FileDrop>
    )

  }
}

DropZone.propTypes = {

  /**
   * The text to display in the dropzone
   */
  text: PropTypes.string
}

export default DropZone;