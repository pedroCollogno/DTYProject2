import React, {Component} from 'react';
import FileDrop from 'react-file-drop';


const styles = { border: '1px solid black', width: 600, color: 'black', padding: 20 };
class DropZone extends Component {


  render() {
    return (
        <div style={{styles}}>
        <FileDrop onDrop={this.props.handleDrop}>
          {this.props.text}
        </FileDrop>
      </div>)
      
  }
}

export default DropZone;