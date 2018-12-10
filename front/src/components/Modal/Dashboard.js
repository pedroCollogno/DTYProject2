import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';

import { Bar, Pie, Bubble, Polar, Doughnut, Line } from 'react-chartjs-2';


class Dashboard extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalState: false,
      networkSelected: 0,
      emittorSelected: null
    };

    this.toggleModal = this.toggleModal.bind(this);
    this.getEmittorList = this.getEmittorList.bind(this);
    this.rainbow = this.rainbow.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.degToDms = this.degToDms.bind(this);
  }

  toggleModal() {
    this.setState((prev, props) => {
      const newState = !prev.modalState;

      return { modalState: newState };
    });
  }


  degToDms(deg) {
    let d = Math.floor(deg);
    let minfloat = (deg - d) * 60;
    let m = Math.floor(minfloat);
    let secfloat = (minfloat - m) * 60;
    let s = Math.round(secfloat);
    // After rounding, the seconds might become 60. These two
    // if-tests are not necessary if no rounding is done.
    if (s == 60) {
      m++;
      s = 0;
    }
    if (m == 60) {
      d++;
      m = 0;
    }
    return ("" + d + "°" + m + "'" + s + '"');
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
    switch (i % 6) {
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

  handleChange(event) {
    this.setState({
      networkSelected: event.target.value
    })
  }

  getEmittorList() {
    var stats = {
      networks: {
        numberEVF: 0,
        numberFF: 0,
        numberBurst: 0,
        numberNetworks: 0
      },
      cycle: {
        progress: 0,
        clusterDuration: 0,
        readDuration: 0
      },
      global : {
        clusterDurationList: [],
        readDurationList: [],
        progressList: [],
        memoryUsageList: [],
        CPUUsageList: []
      },
      emittor: {
        id: null,
        lat: 0,
        lng: 0,
        network: 0
      }
    }
    var networks = this.props.emittors;
    var cycle_mem_info = this.props.cycle_mem_info;
    var global_mem_info = this.props.global_mem_info;

    // The id of each network
    var networksIndex = Object.keys(networks).map((network, i) => (
      i
    ))

    stats.networks.numberNetworks = networksIndex.length

    var networksLengths = []
    var networksTypes = []
    var networksFrequenciesMHz = []

    var emittersNetworksIds = []
    var emittersDurations = []
    var emittersIds = []
    var emitterLat = []
    var emitterLng = []

    console.log(global_mem_info)

    // The total duration
    stats.cycle.progress = cycle_mem_info['progress']
    // The read duration 
    stats.cycle.readDuration = cycle_mem_info['read_duration']
    stats.global.readDurationList = global_mem_info['read_duration_list']
    // The clustering duration
    stats.cycle.clusterDuration = cycle_mem_info['cluster_duration']
    stats.global.clusterDurationList = global_mem_info['cluster_duration_list']
    // Cumulative CPU usage
    stats.global.CPUUsageList = global_mem_info['cpu_usage_list']
    // Cumulative memory usage
    stats.global.memoryUsageList = global_mem_info['mem_usage_list']
    // Progress list since start
    stats.global.progressList = global_mem_info['progress_list']

    Object.keys(networks).forEach(element => {
      // The size of each network
      networksLengths.push(Object.keys(networks[element]).length)
      // The type of emission of each network
      networksTypes.push(Object.values(networks[element])[0]['emission_type'])
      // The central frequency of each network
      networksFrequenciesMHz.push(Object.values(networks[element])[0]['frequency'] / 10e6)

      Object.keys(networks[element]).forEach(i => {
        // The network id of each emittor
        emittersNetworksIds.push(networks[element][i]['network_id']);
        // The duration of each emittor
        emittersDurations.push(networks[element][i]['duration'] / 1e6);
        // The id of each emittor
        emittersIds.push(networks[element][i]['track_id']);
        // The Latitude of each emittor
        emitterLat.push(networks[element][i]['coordinates']['lat'])
        // The Longitude of each emittor
        emitterLng.push(networks[element][i]['coordinates']['lng'])
      })
    });

    // Set default index of emittor selected
    var emittorIndex = emittersIds.indexOf(this.state.emittorSelected) || 0
    stats.emittor.id = emittersIds[emittorIndex]
    stats.emittor.lat = this.degToDms(emitterLat[emittorIndex])
    stats.emittor.lng = this.degToDms(emitterLng[emittorIndex])
    stats.emittor.network = emittersNetworksIds[emittorIndex]

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

    // ---------------- LINE CHART DATA ----------------

    const lineData = {
      labels: stats.global.progressList || [],
      datasets:[{
        label: "Memory",
        borderColor: 'rgba(185, 24, 24, 1)',
        backgroundColor: 'rgba(185, 24, 24, 0.5)',
        data: stats.global.memoryUsageList || [],
        yAxisID: 'memory'
      },
      {
        label: "CPU",
        borderColor: 'rgba(24, 51, 185, 1)',
        backgroundColor: 'rgba(24, 51, 185, 0.5)',
        data: stats.global.CPUUsageList || [],
        yAxisID: 'CPU'
      }]
    }
    
    const lineOptions = {
      scales: {
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Cycle'
          } 
        }],
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Memory Usage (MB)'
          },
          display: true,
          id: 'memory',
          position: 'left'
        },
        {
          scaleLabel: {
            display: true,
            labelString: 'CPU Usage (%)'
          },
          display: true,
          id: 'CPU',
          position: 'right'
        }]
      }
    }

    // ---------------- LINE CHART 2 DATA ----------------

    const lineData2 = {
      labels: stats.global.progressList || [],
      datasets:[{
        label: "Processing",
        borderColor: 'rgba(185, 24, 24, 1)',
        backgroundColor: 'rgba(185, 24, 24, 0.5)',
        data: stats.global.readDurationList || [],
        yAxisID: 'processing'
      },
      {
        label: "Clustering",
        borderColor: 'rgba(24, 51, 185, 1)',
        backgroundColor: 'rgba(24, 51, 185, 0.5)',
        data: stats.global.clusterDurationList || [],
        yAxisID: 'clustering'
      }]
    }
    
    const lineOptions2 = {
      scales: {
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Cycle'
          } 
        }],
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Processing Time (ms)'
          },
          display: true,
          id: 'processing',
          position: 'left'
        },
        {
          scaleLabel: {
            display: true,
            labelString: 'Clustering Duration (ms)'
          },
          display: true,
          id: 'clustering',
          position: 'right'
        }
      ]
      }
    }


    // ---------------- BAR CHART DATA ----------------

    var valuesEVF = []
    var valuesFF = []
    var valuesBurst = []
    for (var i = 0; i < networksIndex.length; i++) {
      if (networksTypes[i] == 1) {
        valuesFF.push(networksLengths[i])
        valuesEVF.push(0)
        valuesBurst.push(0)
        stats.networks.numberFF++
      }
      if (networksTypes[i] == 2) {
        valuesFF.push(0)
        valuesEVF.push(networksLengths[i])
        valuesBurst.push(0)
        stats.networks.numberEVF++
      }
      if (networksTypes[i] == 3) {
        valuesFF.push(0)
        valuesEVF.push(0)
        valuesBurst.push(networksLengths[i])
        stats.networks.numberBurst++
      }
    }

    const barData = {
      labels: networksIndex,
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
          stack: '1',
          data: valuesEVF,
        },
        {
          label: ["Burst"],
          backgroundColor: "green",
          borderColor: "green",
          stack: '1',
          data: valuesBurst,
        }],
    }

    const barOptions = {
      scales: {
        xAxes: [{
          stacked: true,
          scaleLabel: {
            display: true,
            labelString: 'Network ID'
          } 
        }],
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Number of Emittors'
          },
          stacked: true,
          ticks: {
            beginAtZero: true
          },
        }]
      }
    }

    // ---------------- PIE CHART DATA ----------------

    var dataEmittors = {}

    for (var i in emittersNetworksIds) {
      !(emittersNetworksIds[i] in dataEmittors) && (dataEmittors[emittersNetworksIds[i]] = {
        //'pos': [],
        'ids': [],
        'durations': []
      });
      // dataEmittors[emittersNetworksIds[i]]['pos'].push(
      //   {
      //     x: emitterLng[i],
      //     y: emitterLat[i],
      //     r: emittersDurations[i] / (progressDuration*10e3)
      //   }
      // );
      dataEmittors[emittersNetworksIds[i]]['ids'].push(emittersIds[i]);
      dataEmittors[emittersNetworksIds[i]]['durations'].push(emittersDurations[i])
    }


    var pieLabels = dataEmittors[this.state.networkSelected] || { 'ids': [] }
    var pieValues = dataEmittors[this.state.networkSelected] || { 'durations': [] }
    var pieColors = []

    for (var i = 0; i < pieLabels['ids'].length; i++) {
      pieColors.push(this.rainbow(pieLabels['ids'].length, i));
    }


    const pieData = {
      labels: pieLabels['ids'],
      datasets: [{
        data: pieValues['durations'],
        backgroundColor: pieColors,
        hoverBackgroundColor: pieColors
      }]
    }

    const pieOptions = {

    }



    return (
      <div className="column">
        <div className="columns is-multiline">
          {/* <div className="column is-3">
              <div className="panel">
                <p className="panel-heading">
                  All Networks
                        </p>
                <div className="panel-block">
                  < Line ref='linechart' data={lineData}/>
                </div>
              </div>
            </div> */}
          <div className="column is-half">
            <div className="box">
              <div className="level">
                <div className="level-item">
                < Line ref='linechart' data={lineData} options={lineOptions}/>
                </div>
              </div>
            </div>
          </div>
          <div className="column is-half">
            <div className="box">
              <div className="level">
                <div className="level-item">
                < Line ref='linechart' data={lineData2} options={lineOptions2}/>
                </div>
              </div>
            </div>
          </div>
          {/* <div className="column is-third">
            <div className="box">
              <div className="heading">Emittor</div>
              <div className="dashboard title">#{stats.emittor.id}</div>
              <div className="level">
                <div className="level-item">
                  <div className="">
                    <div className="heading">Network</div>
                    <div className="dashboard title is-5">#{stats.emittor.network}</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Latitude</div>
                    <div className="dashboard title is-5">{stats.emittor.lat}</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Longitude</div>
                    <div className="dashboard title is-5">{stats.emittor.lng}</div>
                  </div>
                </div>
              </div>
            </div>
          </div> */}
        </div>

        <div className="columns is-multiline">
          <div className="column is-6">
            <div className="panel">
              <p className="panel-heading">
                All Networks
                      </p>
              <div className="panel-block">
                < Bar ref='barchart' data={barData} options={barOptions} getElementAtEvent={dataset => this.setState({ networkSelected: dataset[0]._index })} />
              </div>
            </div>
          </div>
          <div className="column is-6">
            <div className="panel">
              <p className="panel-heading">
                Network #{this.state.networkSelected} : speaking times
              </p>
              <div className="panel-block">
                < Doughnut data={pieData} options={pieOptions} getElementAtEvent={dataset => this.setState({ emittorSelected: dataset[0]._model.label })} />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  render() {

    return (
      <div className="dashboard-button">
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
