import React, { Component } from 'react';
import Modal from './Modal.js';
import './Dashboard.css';


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
    this.handleChange = this.handleChange.bind(this);
    this.clickEvent = this.clickEvent.bind(this);
    this.degToDms = this.degToDms.bind(this);
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
    console.log(this.props.emitters[0])
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

  getEmitterList() {
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
      emitter: {
        id: null,
        lat: 0,
        lng: 0,
        network: 0
      }
    }
    var networks = this.props.emitters;
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
      // The read duration 
      stats.cycle.readDuration = Object.values(networks[element])[0]['read_duration']
      // The clustering duration
      stats.cycle.clusterDuration = Object.values(networks[element])[0]['cluster_duration']
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
        emittersIds.push(networks[element][i]['track_id']);
        // The Latitude of each emitter
        emitterLat.push(networks[element][i]['coordinates']['lat'])
        // The Longitude of each emitter
        emitterLng.push(networks[element][i]['coordinates']['lng'])
      })
    });

    // Set default index of emitter selected
    var emitterIndex = emittersIds.indexOf(this.state.emitterSelected) || 0
    stats.emitter.id = emittersIds[emitterIndex]
    stats.emitter.lat = this.degToDms(emitterLat[emitterIndex])
    stats.emitter.lng = this.degToDms(emitterLng[emitterIndex])
    stats.emitter.network = emittersNetworksIds[emitterIndex]

    // Gather the durations and ids of emitters, indexed by network id
    // dataEmitters = {
    //   '0' : {
    //     'durations': [firstEmitterDuration, secondEmitterDuration, ...],
    //     'ids': [firstEmitterId, secondEmitterId, ...]
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

    var dataEmitters = {}

    for (var i in emittersNetworksIds) {
      !(emittersNetworksIds[i] in dataEmitters) && (dataEmitters[emittersNetworksIds[i]] = {
        //'pos': [],
        'ids': [],
        'durations': []
      });
      // dataEmitters[emittersNetworksIds[i]]['pos'].push(
      //   {
      //     x: emitterLng[i],
      //     y: emitterLat[i],
      //     r: emittersDurations[i] / (progressDuration*10e3)
      //   }
      // );
      dataEmitters[emittersNetworksIds[i]]['ids'].push(emittersIds[i]);
      dataEmitters[emittersNetworksIds[i]]['durations'].push(emittersDurations[i])
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
    return (
      <div className="column">
        {/* <div className="level">
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
        </div> */}

        <div className="columns is-multiline">
          <div className="column">
            <div className="box">
              <div className="heading">All Networks</div>
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
                    <div className="heading">Data merging</div>
                    <div className="dashboard title is-5">{stats.cycle.readDuration}ms</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Clustering</div>
                    <div className="dashboard title is-5">{stats.cycle.clusterDuration}ms</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="column is-6">
            <div className="box">
              <div className="heading">Emitter</div>
              <div className="dashboard title">#{stats.emitter.id}</div>
              <div className="level">
                <div className="level-item">
                  <div className="">
                    <div className="heading">Network</div>
                    <div className="dashboard title is-5">#{stats.emitter.network}</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Latitude</div>
                    <div className="dashboard title is-5">{stats.emitter.lat}</div>
                  </div>
                </div>
                <div className="level-item">
                  <div className="">
                    <div className="heading">Longitude</div>
                    <div className="dashboard title is-5">{stats.emitter.lng}</div>
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
                < Doughnut data={pieData} getElementAtEvent={dataset => this.setState({emitterSelected: dataset[0]._model.label})}/>
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
            
          </p>
        </Modal>
      </div>
    );
  }
}

export default Dashboard;
