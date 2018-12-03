import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';

import {Bar} from 'react-chartjs-2';


class Dashboard extends Component {
    constructor(props) {
      super(props);
      
      this.state = {
        modalState: false
      };
      
      this.toggleModal = this.toggleModal.bind(this);
      this.getEmittorList = this.getEmittorList.bind(this);
    }
    
    toggleModal() {   
        console.log(this.props.emittors[0]) 
      this.setState((prev, props) => {
        const newState = !prev.modalState;
        
        return { modalState: newState };
      });
    }

    getEmittorList() {
        var networks = this.props.emittors;
        var test = []
        var networksIndex = Object.keys(networks).map((network, i) => (
            i
        ))
        var networksLength = []
        var networksIds = []
        var networksTypes = []
        Object.keys(networks).forEach(element => {
            networksLength.push( Object.keys(networks[element]).length)

            // for (var key in networks[element]) {
            //   if (networks[element].hasOwnProperty(key)) continue;
            //     console.log("coucou")
            //     var emittor = networks[element][key]
            //     for (var prop in emittor) {
            //       if (!emittor.hasOwnProperty(prop)) continue;
            //       console.log(prop);

            //   }
            // }
            
            Object.keys(networks[element]).forEach(i => {
              networksTypes.push(networks[element][i]['emission_type']);
              networksIds.push(networks[element][i]['network_id'])
              
            })
        });
        // Object.keys(networks).map((network, i) => (
        //     if (networks[i]) {
        //         Object.keys(networks[i]).map((emittor, j) =>
        //         console.log(j)
        //     )
        //     }
            
        // ))
        
        
        //console.log(networksLength)



        console.log('networks', networks)
        var data = {
            labels : networksIndex,
            datasets: [{
                label: "My First dataset",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: networksLength,
                }]
        }

        var data2 = {
          labels : networksIds,
          datasets: [{
              label: "My First dataset",
              backgroundColor: 'rgb(255, 99, 132)',
              borderColor: 'rgb(255, 99, 132)',
              data: networksTypes,
              }]
      }

        return(
            <div>
                            < Bar data={data} />
                            < Bar data={data2}/>
        {networks && Object.keys(networks)?
            <ul>
            {Object.keys(networks).map((network, i) => (
              <li className="network" key={i}>

                  {networks[i] && Object.keys(networks[i])?
                  <div>
                  <span className="index">
                      Network: {i} 
                  </span>
                  {Object.keys(networks[i]).map((emittor, j) => (
                      <li className="emittor" key={j}>
                          <span className="index">Emittor: {j}</span>
                      </li>
                  ))}
                  </div>
                  :null}
              </li>
              ))}
            </ul>
            :null}

            </div>)

    }
    
    render() {
        
      return(
          <div>
            <div className="has-text-centered content">
              <a className="button is-blue" onClick={this.toggleModal}>
                Dashboard
              </a>
            </div>
            
            <Modal 
              closeModal={this.toggleModal} 
              modalState={this.state.modalState} 
              title="Dashboard"
            >
              <p>
              {this.getEmittorList()}
              
              </p>
            </Modal>
            </div>
      );
    }
  }

export default Dashboard;
