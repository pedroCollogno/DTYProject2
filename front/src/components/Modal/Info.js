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
      <div className="dashboard-button">
        <div className="has-text-centered content">
          <a className="button is-info" onClick={this.toggleModal}>
            <FontAwesomeIcon icon='info' />
          </a>

        </div>

        <Modal
          closeModal={this.toggleModal}
          modalState={this.state.modalState}
          title='Help'>
          <div className="column">
          <figure class="image is-16x9">
                <img src="https://placehold.it/1280x720"/>
              </figure>
          </div>
        </Modal>
      </div>
    );
  }
}

export default Info;
