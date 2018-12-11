import React, { Component } from 'react';
import Modal from './Modal.js';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'




class Info extends Component {
  constructor(props) {
    super(props);

    this.state = {
    };

    this.toggleModal = this.toggleModal.bind(this);
  }

  toggleModal() {
    this.setState((prev, props) => {
      const newState = !prev.modalState;

      return { modalState: newState };
    });
  }



  render() {

    return (
      <div>
        <span className="button" onClick={this.toggleModal}>
          <span className="icon is-small">
              <FontAwesomeIcon icon='info' />
          </span>
        </span>

        <Modal
          closeModal={this.toggleModal}
          modalState={this.state.modalState}
          title={this.props.title}>
          <div className="column">
          <figure class="image is-16x9">
                <img src={"../../assets/" + this.props.simulationMode + ".jpg"}/>
              </figure>
          </div>
        </Modal>

      </div>
    );
  }
}

export default Info;
