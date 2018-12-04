import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';

import {Bar} from 'react-chartjs-2';


class Dashboard extends Component {
    constructor(props) {
      super(props);
      
      this.state = {
        modalState: false,
        numberNetworks : 0
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
        var networksIndex = Object.keys(networks).map((network, i) => (
            i
        ))
        var networksLength = []

        var emittersNetworksIds = []
        var emittersNetworksTypes = []
        var emittersDurations = []
        var emittersIds = []
        Object.keys(networks).forEach(element => {
            networksLength.push( Object.keys(networks[element]).length)
            
            Object.keys(networks[element]).forEach(i => {
              emittersNetworksTypes.push(networks[element][i]['emission_type']);
              emittersNetworksIds.push(networks[element][i]['network_id']);
              emittersDurations.push(networks[element][i]['duration']);
              emittersIds.push(networks[element][i]['track_id'])
            })
        });

        //this.setState({numberNetworks: networksLength})

        var dataEmittors = {}

        for (var i in emittersNetworksIds) {
          !(emittersNetworksIds[i] in dataEmittors) && (dataEmittors[emittersNetworksIds[i]] = {
            'durations': [],
            'ids': []
          });
          dataEmittors[emittersNetworksIds[i]]['durations'].push(emittersDurations[i]);
          dataEmittors[emittersNetworksIds[i]]['ids'].push(emittersIds[i]);
        }

        console.log('test', dataEmittors)
        console.log('networks', networks)
        var data = {
            labels : networksIndex,
            datasets: [{
                label: "Networks ammount of emittors",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: networksLength,
                }],
                options : {
                  scales: {
                      yAxes: [{
                          display: true,
                          ticks: {
                              beginAtZero: true   // minimum value will be 0.
                          }
                      }]
                  }
              }
        }

        var labels2 = dataEmittors[0] || {'ids':[]}
        var values2 = dataEmittors[0] || {'durations': []}

        var data2 = {
          labels : labels2['ids'],
          datasets: [{
              label: "My First dataset",
              backgroundColor: 'rgb(255, 99, 132)',
              borderColor: 'rgb(255, 99, 132)',
              data: values2['durations'],
              }]

      }

        return(
            <div>
              < Bar data={data}/>
              < Bar data={data2}/>
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
