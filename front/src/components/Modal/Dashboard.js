import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';

import { Bar, Pie, Bubble, Polar, Doughnut } from 'react-chartjs-2';


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
    this.clickEvent = this.clickEvent.bind(this);
  }

  clickEvent(c, i) {
    console.log(c, i)
    // e = i[0];
    // console.log(e._index)
    // var x_value = this.data.labels[e._index];
    // var y_value = this.data.datasets[0].data[e._index];
    // console.log(x_value);
    // console.log(y_value);
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
        progress: 0
      }
    }
    var networks = this.props.emittors;
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

    Object.keys(networks).forEach(element => {
      // The total duration
      stats.cycle.progress = Object.values(networks[element])[0]['progress']
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
      options: {
        'onClick': this.clickEvent(),
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
    return (
      <div className="column">
        <div className="level">
          <div className="level-right">
            <div className="level-item">
              <div className="control">
                <div className="select">
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

        <div className="columns is-multiline">
          <div className="column">
            <div className="box">
              <div className="heading">Number of Networks</div>
              <div className="dashboard title">{stats.networks.numberNetworks}</div>
              <div className="level">
                <div className="level-item">
                  <div className="">
                    <div className="heading">Burst</div>
                    <div className="dashboard title is-5">{stats.networks.numberBurst}</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">FF</div>
                    <div className="dashboard title is-5">{stats.networks.numberFF}</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">EVF</div>
                    <div className="dashboard title is-5">{stats.networks.numberEVF}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="column">
            <div className="box">
              <div className="heading">Cycle</div>
              <div className="dashboard title">#{stats.cycle.progress}</div>
              <div className="level">
                <div className="level-item">
                  <div className="">
                    <div className="heading">Rev Prod $</div>
                    <div className="dashboard title is-5">30%</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Rev Serv $</div>
                    <div className="dashboard title is-5">25%</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Exp %</div>
                    <div className="dashboard title is-5">45%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="column">
            <div className="box">
              <div className="heading">Feedback Activity</div>
              <div className="dashboard title">78% &uarr;</div>
              <div className="level">
                <div className="level-item">
                  <div className="">
                    <div className="heading">Positive</div>
                    <div className="dashboard title is-5">1560</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Negative</div>
                    <div className="dashboard title is-5">368</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Pos/Neg %</div>
                    <div className="dashboard title is-5">77% / 23%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="column">
            <div className="box">
              <div className="heading">Orders / Returns</div>
              <div className="dashboard title">75% / 25%</div>
              <div className="level">
                <div className="level-item">
                  <div className="">
                    <div className="heading">Orders $</div>
                    <div className="dashboard title is-5">425,000</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Returns $</div>
                    <div className="dashboard title is-5">106,250</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Success %</div>
                    <div className="dashboard title is-5">+ 28,5%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="columns is-multiline">
          <div className="column is-6">
            <div className="panel">
              <p className="panel-heading">
                All Networks
                      </p>
              <div className="panel-block">
                < Bar ref='barchart' data={barData} getElementAtEvent={dataset => this.setState({ networkSelected: dataset[0]._index })} />
              </div>
            </div>
          </div>
          <div className="column is-6">
            <div className="panel">
              <p className="panel-heading">
                Network #{this.state.networkSelected}
              </p>
              <div className="panel-block">
                < Doughnut data={pieData} />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  render() {

    return (
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
