import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';

import { Bar, Doughnut, Line } from 'react-chartjs-2';
import 'chartjs-plugin-labels';



class Dashboard extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalState: false,
      networkSelected: 0,
      emitterSelected: null
    };

    this.toggleModal = this.toggleModal.bind(this);
    this.getEmitterList = this.getEmitterList.bind(this);
    this.rainbow = this.rainbow.bind(this);
    this.degToDms = this.degToDms.bind(this);
  }

  /**
   * This function is used to toggle the modal.
   */
  toggleModal() {
    this.setState((prev, props) => {
      const newState = !prev.modalState;

      return { modalState: newState };
    });
  }

  /** 
   * This function is used to convert geoloc to ... ° ... ' ... " 
   * @param {*} deg 
   */
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

  /**
   * This function generates vibrant, "evenly spaced" colours (i.e. no clustering). 
   * @param {Number} numOfSteps 
   * @param {Number} step 
   */
  rainbow(numOfSteps, step) {
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

  /**
  * This function gets all the data (about networks and emitters) from the App component and renders the core of the dashboard.
  */
  getEmitterList() {
    // Some stats displayed in the dahsboard are stored in this object
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
      global: {
        clusterDurationList: [],
        readDurationList: [],
        progressList: [],
        memoryUsageList: [],
        CPUUsageList: []
      }
    }
    // We get the data from the props (from app component)
    var networks = this.props.emitters;
    var cycle_mem_info = this.props.cycle_mem_info;
    var global_mem_info = this.props.global_mem_info;

    // Array containing all the ids of the networks : [0, 1, 2 ..., n]
    var networksIndex = Object.keys(networks).map((network, i) => (
      i + 1
    ))

    // Number of networks
    stats.networks.numberNetworks = networksIndex.length

    var networksLengths = []
    var networksTypes = []
    var networksFrequenciesMHz = []

    var emittersNetworksIds = []
    var emittersDurations = []
    var emittersIds = []
    var emitterLat = []
    var emitterLng = []

    // The total duration
    stats.cycle.progress = cycle_mem_info['progress']
    // The read duration 
    stats.cycle.readDuration = cycle_mem_info['read_duration']
    stats.global.readDurationList = global_mem_info['read_duration_list']
    // The clustering duration
    stats.cycle.clusterDuration = cycle_mem_info['cluster_duration']
    stats.global.clusterDurationList = global_mem_info['cluster_duration_list']
    // Cumulative CPU usage
    stats.global.CPUUsageList = global_mem_info['cpu_usage_list'] || []
    // Set the max value at 100% ...
    for (var i = 0; i < stats.global.CPUUsageList.length; i++) {
      if (stats.global.CPUUsageList[i] > 100) {
        stats.global.CPUUsageList[i] = 100
      }
    }
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
        // The network id of each emitter
        emittersNetworksIds.push(networks[element][i]['network_id']);
        // The duration of each emitter
        emittersDurations.push(networks[element][i]['duration'] / 1e6);
        // The id of each emitter
        emittersIds.push(networks[element][i]['id']);
        // The Latitude of each emitter
        emitterLat.push(networks[element][i]['coordinates']['lat'])
        // The Longitude of each emitter
        emitterLng.push(networks[element][i]['coordinates']['lng'])
      })
    });

    // ---------------- LINE CHART DATA ----------------

    // Data for the first line chart : CPU and Memory usages

    const lineData = {
      labels: stats.global.progressList || [],
      datasets: [{
        label: "Memory",
        borderColor: 'rgba(135,206,250,1)',
        backgroundColor: 'rgba(135,206,250,0.5)',
        data: stats.global.memoryUsageList || [],
        yAxisID: 'memory'
      },
      {
        label: "CPU",
        borderColor: 'rgba(106,90,205,1)',
        backgroundColor: 'rgba(106,90,205,0.5)',
        data: stats.global.CPUUsageList || [],
        yAxisID: 'CPU'
      }]
    }

    const lineOptions = {
      title: {
        display: true,
        text: 'Computer ressources usage'
      },
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
          position: 'left',
          ticks: {
            min: 0
          }
        },
        {
          scaleLabel: {
            display: true,
            labelString: 'CPU Usage (%)'
          },
          display: true,
          id: 'CPU',
          position: 'right',
          ticks: {
            min: 0,
            max: 100
          }
        }]
      }
    }

    // ---------------- LINE CHART 2 DATA ----------------

    // Data for the second line chart : Processing and Clustering times

    const lineData2 = {
      labels: stats.global.progressList || [],
      datasets: [{
        label: "Processing",
        borderColor: 'rgba(255,99,71,1)',
        backgroundColor: 'rgba(255,99,71,0.5)',
        data: stats.global.readDurationList || [],
        yAxisID: 'processing'
      },
      {
        label: "Clustering",
        borderColor: 'rgba(255,165,0,1)',
        backgroundColor: 'rgba(255,165,0,0.5)',
        data: stats.global.clusterDurationList || [],
        yAxisID: 'clustering'
      }]
    }

    const lineOptions2 = {
      title: {
        display: true,
        text: 'Process execution time'
      },
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
          position: 'left',
          ticks: {
            max: Math.max(...(stats.global.readDurationList || [1])) * 1.5
          }
        },
        {
          scaleLabel: {
            display: true,
            labelString: 'Clustering Time (ms)'
          },
          display: true,
          id: 'clustering',
          position: 'right'
        }
        ]
      }
    }


    // ---------------- BAR CHART DATA ----------------

    // Data for the bar chart

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
      title: {
        display: true,
        text: 'Number of emitters per Network'
      },
      plugins: {
        labels: {
          render: 'value',
          fontColor: 'rgba(0, 0, 0, 0)'
        }
      },
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
            labelString: 'Number of Emitters'
          },
          stacked: true,
          ticks: {
            beginAtZero: true
          },
        }]
      }
    }

    // ---------------- PIE CHART DATA ----------------

    // Data for the pie chart

    // Gather the durations and ids of emitters, indexed by network id
    // dataEmitters = {
    //   '0' : {
    //     'durations': [firstEmitterDuration, secondEmitterDuration, ...],
    //     'ids': [firstEmitterId, secondEmitterId, ...]
    //     'totalDuration' : int
    //   },
    //   '1' : {
    //     ...
    //   }
    //   ...
    // }

    var dataEmitters = {}

    for (var i in emittersNetworksIds) {
      !(emittersNetworksIds[i] in dataEmitters) && (dataEmitters[emittersNetworksIds[i]] = {
        'ids': [],
        'durations': [],
        'totalDuration': 0
      });
      dataEmitters[emittersNetworksIds[i]]['ids'].push(emittersIds[i]);
      dataEmitters[emittersNetworksIds[i]]['durations'].push(emittersDurations[i])
      dataEmitters[emittersNetworksIds[i]]['totalDuration'] += emittersDurations[i]
    }


    var pieLabels = dataEmitters[this.state.networkSelected] || { 'ids': [] }
    var pieValues = dataEmitters[this.state.networkSelected] || { 'durations': [] }
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
      title: {
        display: true,
        text: 'Speaking time of each emitter in Network ' + this.state.networkSelected + ' - Total spoken time : ' + Math.round((dataEmitters[this.state.networkSelected] || { 'totalDuration': 0 })['totalDuration']) + ' seconds'
      },
      plugins: {
        labels: {
          render: 'percentage',
          fontColor: '#000',
          position: 'outside'
        }
      },
      tooltips: {
        mode: 'label',
        callbacks: {
          label: function (tooltipItem, data) {
            var indice = tooltipItem.index;
            return data.labels[indice] + ': ' + data.datasets[0].data[indice] + ' seconds';
          }
        }
      }
    }

    return (
      <div className="column">
        <div class="level">
          <div class="level-item has-text-centered">
            <div>
              <p class="dashboard subtitle">Method</p>
              <p class="dashboard title">{(this.props.simulationMode) || 'No method selected'}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="dashboard subtitle">Time</p>
              <p class="dashboard title">{(this.props.cycle_mem_info['progress']) || 0} sec</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="dashboard subtitle">Number of Emitters</p>
              <p class="dashboard title">{emittersIds.length}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="dashboard subtitle">EVF Networks</p>
              <p class="dashboard title">{stats.networks.numberEVF}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="dashboard subtitle">FF Networks</p>
              <p class="dashboard title">{stats.networks.numberFF}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="dashboard subtitle">Burst Networks</p>
              <p class="dashboard title">{stats.networks.numberBurst}</p>
            </div>
          </div>
        </div>
        <div className="columns is-multiline">
          <div className="column is-half">
            <div className="box">
              <div className="level">
                <div className="level-item">
                  < Line ref='linechart' data={lineData} options={lineOptions} />
                </div>
              </div>
            </div>
          </div>
          <div className="column is-half">
            <div className="box">
              <div className="level">
                <div className="level-item">
                  < Line ref='linechart' data={lineData2} options={lineOptions2} />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="columns is-multiline">
          <div className="column is-half">
            <div className="box">
              <div className="level">
                <div className="level-item">
                  < Bar ref='barchart' data={barData} options={barOptions} getElementAtEvent={dataset => this.setState({ networkSelected: dataset[0]._index })} />
                </div>
              </div>
            </div>
          </div>
          <div className="column is-half">
            <div className="box">
              <div className="level">
                <div className="level-item">
                  < Doughnut data={pieData} options={pieOptions} getElementAtEvent={dataset => this.setState({ emitterSelected: dataset[0]._model.label })} />
                </div>
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
          title='Dashboard'>
          <p>
            {this.getEmitterList()}
          </p>
        </Modal>
      </div>
    );
  }
}

export default Dashboard;
