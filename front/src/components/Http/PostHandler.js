import React, { Component } from "react";
import axios from "axios";
import DropZone from "./Drag&Drop";
import './PostHandler.css';
import PropTypes from "prop-types";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

class HttpRequestHandler extends Component {

    constructor(props) {
        super(props);
        this.state = {
            files: [], // Contains all the uploaded files
            savedFiles: [], // copy of the uploaded files to easily switch simulation modes
            fileNames: {}, // Contains all the uploaded files names (useful to avoid posting the same file twice)
            loaded: false, // Did the posting of the files go well ?
            dropText: "Or drop your .PRP files here !", // Text to display in the drop zone
            inputFiles: [],
            progress: 0,
            total_duration: 0,
            playing: true
        };
        this.postFiles = this.postFiles.bind(this); // functions allowed to update the state of the component
        this.onChange = this.onChange.bind(this);
        this.fileUpload = this.fileUpload.bind(this);
        this.onDrop = this.onDrop.bind(this);
        this.reset = this.reset.bind(this);
        this.play = this.play.bind(this);
        this.pause = this.pause.bind(this);
        this.stop = this.stop.bind(this);
        this.onStart = this.onStart.bind(this);
        this.onStartML = this.onStartML.bind(this);
        this.onStartDL = this.onStartDL.bind(this);
        this.onStartMix = this.onStartMix.bind(this);
    }

    /**
     * Called when the form is submitted. Posts the data and checks the response of the backend
     * @param {*} e 
     */
    onFormSubmit(e) {
        e.preventDefault() // Stops form submit
        this.postFiles(this.state.files);
    }

    postFiles(files) {
        this.fileUpload(files).then((res1) => {
            console.log(res1.data); // Should be "POST ok !"
            if (res1.data === "POST ok !") {
                axios.get("http://localhost:8000/getstations") // GETs the locations of the reception stations...
                    .then((res2) => {
                        this.props.getStations(res2); // ...and update the App.js state !
                        axios.get("http://localhost:8000/emittorspositions")
                            .then((res3) => {
                                if (res3.data) {
                                    this.props.getEmittorsPositions(res3);
                                    this.setState({ loaded: true }); // Allows the "Start simulation" button to be active 
                                }
                            });
                    });
            }
        });
    }

    /**
     * When entering files with the input button, updates the state of the component (pre-loads them).
     * @param {*} e 
     */
    onChange(e) {
        for (let f of e.target.files) {
            if (!this.state.fileNames[f.name]) {
                let dic = JSON.parse(JSON.stringify(this.state.fileNames));
                dic[f.name] = 1;
                let array = this.state.files;
                array.push(f);
                this.setState({ files: array, fileNames: dic });
            }
        }
    }

    /**
     * Triggered when the "Just run" button is pushed. Starts the simulation. 
     * @param {*} e 
     */
    onStart(e) {
        axios.get("http://localhost:8000/startsimulation")
            .then((res) => {
                console.log("Simulation started !");
                this.props.changeSimulationMode("Running simulation");
            });
    }

    /**
     * Triggered when the "Simulation with both techniques" button is pushed. Starts the simulation. 
     * @param {*} e 
     */
    onStartMix(e) {
        axios.get("http://localhost:8000/startsimulationMix")
            .then((res) => {
                console.log("Simulation started !");
                this.props.changeSimulationMode("Clustering + Emittor-to-Cluster DL");
            });
    }

    /**
     * Triggered when the "Simulation with Clustering" only button is pushed. Starts the simulation.
     * @param {*} e 
     */
    onStartML(e) {
        axios.get("http://localhost:8000/startsimulationML")
            .then((res) => {
                console.log("Simulation started using only DB_SCAN for clustering !");
                this.props.changeSimulationMode("Clustering");
            });
    }

    /**
     * Triggered when the "Simulation with Deep Learning only" button is pushed. Starts the simulation.
     * @param {*} e 
     */
    onStartDL(e) {
        axios.get("http://localhost:8000/startsimulationDL")
            .then((res) => {
                console.log("Simulation started using only Deep Learning for clustering !");
                this.props.changeSimulationMode("Emittor-to-Emittor DL");
            });
    }

    /**
     * POSTs the entered files to the backend.
     * The files should be stored in an array.
     * @param {*} files 
     */
    fileUpload(files) {
        return this.reset()
            .then((res) => {
                const url = 'http://localhost:8000/upload'; // server route to POST request
                const formData = new FormData();
                let i = 0;
                for (let file of files) {
                    formData.append("File" + i, file, file.name); // standardized name for formData entry : "File{i}" (Django)
                    i += 1;
                }
                const config = {
                    headers: {
                        'content-type': 'multipart/form-data'
                    }
                }

                return axios.post(url, formData, config) // sends POST request
            })

    }

    /**
     * When entering a file with the drag&drop zone, updates the state of the component (pre-loads it).
     * @param {*} file
     * @param {*} e 
     */
    onDrop(file, e) {
        if (file) {
            for (let f of file) { // file is an iterator containing the actual file f
                if (!this.state.fileNames[f.name]) { // if the file has not already been entered
                    let dic = JSON.parse(JSON.stringify(this.state.fileNames));
                    dic[f.name] = 1;
                    let array = this.state.files;
                    array.push(f);
                    let text = "" + array.length + " files dropped.";
                    this.setState({ files: array, dropText: text, fileNames: dic });
                }
            }
        }
    }

    /**
     * Handles any error that might happen when resetting the simulation.
     * @param {*} error 
     */
    handleResetError(error) {
        // Error
        if (error.response) {
            if (error.response.status == 500) { // Reset even if backend has internal error while resetting
                console.log("Simulation stopped, even though backend ran into internal error (500) !");
                this.setState({
                    files: [],
                    fileNames: {},
                    loaded: false,
                    dropText: "Or drop your .PRP files here !",
                    inputFiles: []
                });
                this.props.reset();
            } else {
                console.log(error.response.data);
                console.log(error.response.status);
                console.log(error.response.headers);
            }
        } else if (error.request) { // Reset even if backend is down
            console.log("Simulation stopped, even though backend was down !");
            this.setState({
                files: [],
                fileNames: {},
                loaded: false,
                dropText: "Or drop your .PRP files here !",
                inputFiles: []
            });
            this.props.reset();
        } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', error.message);
        }
    }

    /**
     * Resets the environment. (stops backends processing of data)
     */
    reset() {
        this.props.changeSimulationMode("");
        return axios.get("http://localhost:8000/stopsimulation")
            .then((res) => {
                console.log("Simulation stopped !");
                if (this.state.savedFiles.length == 0) {
                    this.setState({ savedFiles: this.state.files });
                }
                this.setState({
                    files: [],
                    fileNames: {},
                    loaded: false,
                    dropText: "Or drop your .PRP files here !",
                    inputFiles: []
                });
                this.props.reset();
            })
            .catch((error) => {
                this.handleResetError(error);
            });
    }

    play() {
        this.setState({ playing: true });
        axios.get("http://localhost:8000/playsimulation")
            .then((res) => {
                console.log("Simulation restarting after pause !");
            });
    }

    pause() {
        this.setState({ playing: false });
        axios.get("http://localhost:8000/pausesimulation")
            .then((res) => {
                console.log("Simulation paused !");
            });
    }

    stop() {
        this.postFiles(this.state.savedFiles);
    }

    /**
     * Updates the progress bar.
     * @param {*} nextProps 
     */
    componentWillReceiveProps(nextProps) {
        if (nextProps != this.props) {
            this.setState({
                progress: nextProps.cycle_mem_info.progress,
                total_duration: nextProps.cycle_mem_info.total_duration
            })
        }
    }


    getProgressStart() {
        let delta = "0:00"
        let hour_append = "";
        let min_append = "";
        let sec_append = "";
        if (this.state.progress) {
            let d = new Date()
            let date_delta = new Date(this.state.progress * 1000 + d.getTimezoneOffset() * 60000)

            if (date_delta.getHours()) {
                hour_append = date_delta.getHours() + ":";
            }
            if (date_delta.getMinutes() < 10 && date_delta.getHours()) {
                min_append = "0" + date_delta.getMinutes() + ":";
            } else {
                min_append = date_delta.getMinutes() + ":";
            }

            if (date_delta.getSeconds() < 10) {
                sec_append = "0" + date_delta.getSeconds();
            } else {
                sec_append = date_delta.getSeconds();
            }
            delta = hour_append + min_append + sec_append
        }
        return delta
    }


    getProgressEnd() {
        let delta = "0:00"
        let hour_append = "";
        let min_append = "";
        let sec_append = "";
        if (this.state.total_duration) {
            let d = new Date()
            let date_delta = new Date(this.state.total_duration * 1000 + d.getTimezoneOffset() * 60000)

            if (date_delta.getHours()) {
                hour_append = date_delta.getHours() + ":";
            }
            if (date_delta.getMinutes() < 10 && date_delta.getHours()) {
                min_append = "0" + date_delta.getMinutes() + ":";
            } else {
                min_append = date_delta.getMinutes() + ":";
            }

            if (date_delta.getSeconds() < 10) {
                sec_append = "0" + date_delta.getSeconds();
            } else {
                sec_append = date_delta.getSeconds();
            }
            delta = hour_append + min_append + sec_append
        }
        return delta
    }

    render() {
        return (
            <div>
                <form onSubmit={(e) => this.onFormSubmit(e)}>
                    <div className="tile is-ancestor is-vertical">
                        <div className="tile">
                            <div className="tile is-parent" id="upload-tile">
                                <article className="tile is-child">
                                    <div className="file has-name is-boxed is-centered is-fullwidth" >
                                        <label className="file-label" >
                                            <input type="file" className="file-input" multiple
                                                onChange={this.onChange} value={this.state.inputFiles} />
                                            <span className="button is-grey" id="upload-button">
                                                <span className="icon">
                                                    <FontAwesomeIcon icon='download' />
                                                </span>
                                                <span>Upload your .PRP files…</span>
                                            </span>
                                            <span className="file-name has-text-white-ter" >
                                                {this.state.files.toString()}
                                            </span>
                                        </label>
                                    </div>
                                </article>
                                <article className="tile is-child">
                                    {/* Handles the drag&drop area */}
                                    <DropZone handleDrop={this.onDrop} text={this.state.dropText} />
                                </article>
                            </div>
                            <div className="tile is-parent">
                                <article className="tile is-child">
                                    <div className="file has-name is-boxed is-centered is-fullwidth right-buttons">
                                        <label className="file-label" >
                                            <button type="submit" className="button is-blue" >
                                                <span className="file-icon">
                                                    <FontAwesomeIcon icon='upload' />
                                                </span>
                                                <span>Upload</span>
                                            </button>
                                        </label>
                                    </div>
                                </article>
                                <article className="tile is-child">
                                    <div className="file has-name is-boxed is-centered is-fullwidth right-buttons" >
                                        <label className="file-label" >
                                            <button type="button" className="button is-danger" onClick={this.reset}>
                                                <span className="file-icon">
                                                    <FontAwesomeIcon icon='undo' />
                                                </span>
                                                <span>Reset</span>
                                            </button>

                                        </label>
                                    </div>
                                </article>
                            </div>
                        </div>
                    </div>
                </form>
                <section className="control-section">
                    <a className="button item" onClick={this.play} disabled={this.state.playing || !this.state.loaded}>
                        <span className="icon is-small" >
                            <FontAwesomeIcon icon='play' />
                        </span>
                    </a>
                    <a className="button item" onClick={this.pause} disabled={!this.state.playing || !this.state.loaded}>
                        <span className="icon is-small">
                            <FontAwesomeIcon icon='pause' />
                        </span>
                    </a>
                    <a className="button item" onClick={this.stop} disabled={!this.state.loaded}>
                        <span className="icon is-small">
                            <FontAwesomeIcon icon='stop' />
                        </span>
                    </a>
                    <span className="button time-before">{this.getProgressStart()}</span>
                    <progress className="progress is-medium is-blue" value={this.state.progress} max={this.state.total_duration}></progress>
                    <span className="button time-after">{this.getProgressEnd()}</span>
                </section>
                {/* "Start simulation" button, active if the posting of the files went ok */}
                <section className="simulation">
                    <div className="columns">
                        <div className="buttons has-addons column">
                            <span className="button" id="start-sim-button" disabled={!this.state.loaded} onClick={this.onStart}>
                                <span className="file-icon">
                                    <FontAwesomeIcon icon='magic' />
                                </span>
                                Just Run
                            </span>
                            <span className="button">
                                <span className="icon is-small">
                                    <FontAwesomeIcon icon='info' />
                                </span>
                            </span>
                        </div>
                        <div className="buttons has-addons column">
                            <span className="button" id="start-sim-ml-button" disabled={!this.state.loaded} onClick={this.onStartML}>
                                <span className="file-icon">
                                    <FontAwesomeIcon icon='magic' />
                                </span>
                                Clustering
                            </span>
                            <span className="button">
                                <span className="icon is-small">
                                    <FontAwesomeIcon icon='info' />
                                </span>
                            </span>
                        </div>
                        <div className="buttons has-addons column">
                            <span className="button" id="start-sim-dl-button" disabled={!this.state.loaded} onClick={this.onStartDL}>
                                <span className="file-icon">
                                    <FontAwesomeIcon icon='magic' />
                                </span>
                                Emittor-to-Emittor DL
                                </span>
                            <span className="button">
                                <span className="icon is-small">
                                    <FontAwesomeIcon icon='info' />
                                </span>
                            </span>
                        </div>
                        <div className="buttons has-addons column">
                            <span className="button" id="start-sim-button" disabled={!this.state.loaded} onClick={this.onStartMix}>
                                <span className="file-icon">
                                    <FontAwesomeIcon icon='magic' />
                                </span>
                                Clustering + Emittor-to-Cluster DL
                                </span>
                            <span className="button">
                                <span className="icon is-small">
                                    <FontAwesomeIcon icon='info' />
                                </span>
                            </span>
                        </div>
                    </div>
                </section>
            </div>
        )
    }
}

HttpRequestHandler.propTypes = {
    /**
     * The function to handle the HTTP response of the backend (supposedly containing the reception stations)
     */
    getStations: PropTypes.func.isRequired
}

export default HttpRequestHandler;