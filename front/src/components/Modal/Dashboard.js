import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';

import {Bar, Pie, Bubble, Polar, Doughnut} from 'react-chartjs-2';


class Dashboard extends Component {
    constructor(props) {
      super(props);
      
      this.state = {
        modalState: false,
        networkSelected: 0
      };
      
      this.toggleModal = this.toggleModal.bind(this);
      this.getEmittorList = this.getEmittorList.bind(this);
      this.rainbow = this.rainbow.bind(this);
      this.handleChange = this.handleChange.bind(this);
    }
    
    toggleModal() {   
      console.log(this.props.emittors[0]) 
      this.setState((prev, props) => {
        const newState = !prev.modalState;
        
        return { modalState: newState };
      });
    }

    rainbow(numOfSteps, step) {
      // This function generates vibrant, "evenly spaced" colours (i.e. no clustering). This is ideal for creating easily distinguishable vibrant markers in Google Maps and other apps.
      // Adam Cole, 2011-Sept-14
      // HSV to RBG adapted from: http://mjijackson.com/2008/02/rgb-to-hsl-and-rgb-to-hsv-color-model-conversion-algorithms-in-javascript
      var r, g, b;
      var h = step / numOfSteps;
      var i = ~~(h * 6);
      var f = h * 6 - i;
      var q = 1 - f;
      switch(i % 6){
          case 0: r = 1; g = f; b = 0; break;
          case 1: r = q; g = 1; b = 0; break;
          case 2: r = 0; g = 1; b = f; break;
          case 3: r = 0; g = q; b = 1; break;
          case 4: r = f; g = 0; b = 1; break;
          case 5: r = 1; g = 0; b = q; break;
      }
      var c = "#" + ("00" + (~ ~(r * 255)).toString(16)).slice(-2) + ("00" + (~ ~(g * 255)).toString(16)).slice(-2) + ("00" + (~ ~(b * 255)).toString(16)).slice(-2);
      return (c);
    }

    handleChange (event) {
      this.setState({
          networkSelected: event.target.value
      })
    }

    getEmittorList() {
        var networks = this.props.emittors;
        // The id of each network
        var networksIndex = Object.keys(networks).map((network, i) => (
            i
        ))

        var networksLengths = []
        var networksTypes = []
        var networksFrequenciesMHz = []

        var emittersNetworksIds = []
        var emittersDurations = []
        var emittersIds = []
        var emitterLat = []
        var emitterLng = []

        var progressDuration = []

        Object.keys(networks).forEach(element => {
            // The total duration
            progressDuration = Object.values(networks[element])[0]['progress']
            // The size of each network
            networksLengths.push(Object.keys(networks[element]).length)
            // The type of emission of each network
            networksTypes.push(Object.values(networks[element])[0]['emission_type'])
            // The central frequency of each network
            networksFrequenciesMHz.push(Object.values(networks[element])[0]['frequency']/10e6)

            Object.keys(networks[element]).forEach(i => {
              // The network id of each emittor
              emittersNetworksIds.push(networks[element][i]['network_id']);
              // The duration of each emittor
              emittersDurations.push(networks[element][i]['duration']/10e6);
              // The id of each emittor
              emittersIds.push(networks[element][i]['track_id']);
              // The Latitude of each emittor
              emitterLat.push(networks[element][i]['coordinates']['lat'])
              // The Longitude of each emittor
              emitterLng.push(networks[element][i]['coordinates']['lng'])
            })
        });

        // Gather the durations and ids of emittors, indexed by network id
        // dataEmittors = {
        //   '0' : {
        //     'durations': [firstEmittorDuration, secondEmittorDuration, ...],
        //     'ids': [firstEmittorId, secondEmittorId, ...]
        //   },
        //   '1' : {
        //     ...
        //   }
        //   ...
        // }

        console.log('networks', networks)

        var valuesEVF = []
        var valuesFF = []
        var valuesBurst = []
        for (var i=0; i<networksIndex.length; i++) {
          if (networksTypes[i] == 1) {
            valuesFF.push(networksLengths[i])
            valuesEVF.push(0)
            valuesBurst.push(0)
          }
          if (networksTypes[i] == 2) {
            valuesFF.push(0)
            valuesEVF.push(networksLengths[i])
            valuesBurst.push(0)          
          }
          if (networksTypes[i] == 3) {
            valuesFF.push(0)
            valuesEVF.push(0)
            valuesBurst.push(networksLengths[i])      
          }
        }

        const barData = {
            labels : networksIndex,
            datasets: [
              {
                label: ["FF"],
                backgroundColor: "blue",
                borderColor: "blue",
                stack: '1',
                data: valuesFF,
              },
              {
                label: ["EVF"],
                backgroundColor: "red",
                borderColor: "red",
                stack :'1',
                data: valuesEVF,
              },
              {
                label: ["Burst"],
                backgroundColor: "green",
                borderColor: "green",
                stack: '1',
                data: valuesBurst,
              }],
              options: {
                scales: {
                  xAxes: [{
                    stacked: true,
                  }],
                  yAxes: [{
                    stacked: true,
                    ticks: {
                      beginAtZero: true
                    },
                  }]
                }
              }
        }

        // var bubbleXYR = []
        // for (var i = 0; i<networksIndex.length; i++) {
        //   bubbleXYR.push({
        //     x: networksIndex[i],
        //     y: networksFrequenciesMHz[i],
        //     r: networksLengths[i]
        //   })
        // }

        // const bubbleData = { 
        //     labels : "test",
        //     datasets: [{
        //         label: "Networks ammount of emittors",
        //         backgroundColor: "blue",
        //         borderColor: "blue",
        //         data: bubbleXYR,
        //         }]
        // }

        // console.log(bubbleXYR)

        var dataEmittors = {}

        for (var i in emittersNetworksIds) {
          !(emittersNetworksIds[i] in dataEmittors) && (dataEmittors[emittersNetworksIds[i]] = {
            'pos': [],
            'ids': [],
            'durations': []
          });
          dataEmittors[emittersNetworksIds[i]]['pos'].push(
            {
              x: emitterLng[i],
              y: emitterLat[i],
              r: emittersDurations[i] / (progressDuration*10e3)
            }
          );
          dataEmittors[emittersNetworksIds[i]]['ids'].push(emittersIds[i]);
          dataEmittors[emittersNetworksIds[i]]['durations'].push(emittersDurations[i])
        }

        console.log(dataEmittors)

        var pieLabels = dataEmittors[this.state.networkSelected] || {'ids': []}
        var pieValues = dataEmittors[this.state.networkSelected] || {'durations': []}
        var pieColors = []

        for (var i = 0; i < pieLabels['ids'].length; i++) {
          pieColors.push(this.rainbow(pieLabels['ids'].length, i));
        }

        var bubbleValues = dataEmittors[this.state.networkSelected] || {'pos': []}

        const bubbleData = { 
            labels : this.state.networkSelected,
            datasets: [{
                label: "Networks ammount of emittors",
                backgroundColor: "blue",
                borderColor: "blue",
                data: bubbleValues['pos']
                }],
            options:{
              scales:{
                xAxes:[{
                  ticks: {
                    stepSize:0.5
                  }
                }],
                yAxes:[{
                  ticks: {
                    stepSize:0.5
                  }
                }]
              }
            }
        }

        const pieData = {
          labels: pieLabels['ids'],
          datasets: [{
            data: pieValues['durations'],
            backgroundColor: pieColors,
            hoverBackgroundColor: pieColors
          }]
        }

        const polarData = {
          labels: pieLabels['ids'],
          datasets: [{
            data: pieValues['durations'],
            backgroundColor: pieColors,
            hoverBackgroundColor: pieColors
          }]
        }

        return(
              <div class="column">
                <div class="level">
                  <div class="level-left">
                    <div class="level-item">
                      <div class="dashboard title">Dashboard</div>
                    </div>
                  </div>
                  <div class="level-right">
                    <div class="level-item">
                      <div class="control">
                        <div class="select">
                          <select value={this.state.networkSelected} onChange={this.handleChange}>
                          {networksIndex.map((i) => {
                            return (<option value={i} key={i}>{i}</option>)
                          })}
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="columns is-multiline">
                  <div class="column">
                    <div class="box">
                      <div class="heading">Number of Networks</div>
                      <div class="dashboard title">{networksIndex.length}</div>
                      <div class="level">
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Burst</div>
                            <div class="dashboard title is-5">250,000</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">FF</div>
                            <div class="dashboard title is-5">750,000</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">EVF</div>
                            <div class="dashboard title is-5">25%</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="column">
                    <div class="box">
                      <div class="heading">Revenue / Expenses</div>
                      <div class="dashboard title">55% / 45%</div>
                      <div class="level">
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Rev Prod $</div>
                            <div class="dashboard title is-5">30%</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Rev Serv $</div>
                            <div class="dashboard title is-5">25%</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Exp %</div>
                            <div class="dashboard title is-5">45%</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="column">
                    <div class="box">
                      <div class="heading">Feedback Activity</div>
                      <div class="dashboard title">78% &uarr;</div>
                      <div class="level">
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Positive</div>
                            <div class="dashboard title is-5">1560</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Negative</div>
                            <div class="dashboard title is-5">368</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Pos/Neg %</div>
                            <div class="dashboard title is-5">77% / 23%</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="column">
                    <div class="box">
                      <div class="heading">Orders / Returns</div>
                      <div class="dashboard title">75% / 25%</div>
                      <div class="level">
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Orders $</div>
                            <div class="dashboard title is-5">425,000</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Returns $</div>
                            <div class="dashboard title is-5">106,250</div>
                          </div>
                        </div>
                        <div class="level-item">
                          <div class="">
                            <div class="heading">Success %</div>
                            <div class="dashboard title is-5">+ 28,5%</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

              <div class="columns is-multiline">
                <div class="column is-6">
                  <div class="panel">
                    <p class="panel-heading">
                      All Networks
                    </p>
                    <div class="panel-block">
                        < Bar data={barData}/>

                    </div>
                  </div>
                </div>
                <div class="column is-6">
                  <div class="panel">
                    <p class="panel-heading">
                      Network #{this.state.networkSelected}
                    </p>
                    <div class="panel-block">
                      < Doughnut data={pieData}/>
                    </div>
                  </div>
                </div>
              </div>
              
              </div>

            )

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
