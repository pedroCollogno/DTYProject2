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
            fileNames: {}, // Contains all the uploaded files names (useful to avoid posting the same file twice)
            loaded: false, // Did the posting of the files go well ?
            dropText: "Or drop your .PRP files here !", // Text to display in the drop zone
            inputFiles: []
        };
        this.onFormSubmit = this.onFormSubmit.bind(this); // functions allowed to update the state of the component
        this.onChange = this.onChange.bind(this);
        this.fileUpload = this.fileUpload.bind(this);
        this.onDrop = this.onDrop.bind(this);
        this.reset = this.reset.bind(this);
    }

    /**
     * Called when the from is submitted. Posts the data and checks the response of the backend
     * @param {*} e 
     */
    onFormSubmit(e) {
        e.preventDefault() // Stops form submit
        this.fileUpload(this.state.files).then((response) => {
            console.log(response.data); // Should be "POST ok !"
            if (response.data === "POST ok !") {
                axios.get("http://localhost:8000/getstations") // GETs the locations of the reception stations...
                    .then((response) => {
                        this.props.getStations(response); // ...and update the App.js state !
                        this.setState({ loaded: true }); // Allows the "Start simulation" button to be active 
                    });
            }
        })
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
     * Triggered when the "Simulation with both techniques" button is pushed. Starts the simulation. 
     * @param {*} e 
     */
    onStart(e) {
        axios.get("http://localhost:8000/startsimulation")
            .then((res) => console.log("Simulation started !"));
    }

    /**
 * Triggered when the "Simulation with Clustering" only button is pushed. Starts the simulation.
 * @param {*} e 
 */
    onStartML(e) {
        axios.get("http://localhost:8000/startsimulationML")
            .then((res) => console.log("Simulation started !"));
    }

    /**
 * Triggered when the "Simulation with Deep Learning only" button is pushed. Starts the simulation.
 * @param {*} e 
 */
    onStartDL(e) {
        axios.get("http://localhost:8000/startsimulationDL")
            .then((res) => console.log("Simulation started !"));
    }

    /**
     * POSTs the entered files to the backend.
     * The files should be stored in an array.
     * @param {*} files 
     */
    fileUpload(files) {
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

    reset() {
        this.setState({
            files: [],
            fileNames: {},
            loaded: false,
            dropText: "Or drop your .PRP files here !",
            inputFiles: []
        });
        this.props.reset();
    }

    render() {
        return (
            <div>
                <form onSubmit={this.onFormSubmit}>

                    <div className="tile is-ancestor is-vertical">
                        <div className="tile">

                            <div className="tile is-parent" >
                                <article className="tile is-child notification">
                                    <div className="file has-name is-boxed is-centered is-fullwidth" >

                                        <label className="file-label" >
                                            <input type="file" className="file-input" multiple
                                                onChange={this.onChange} value={this.state.inputFiles} />
                                            <span className="file-cta">
                                                <span className="file-icon">
                                                    <FontAwesomeIcon icon='download' />
                                                </span>
                                                <span className="file-label">Upload your .PRP files…</span>
                                            </span>
                                            <span className="file-name has-text-white-ter" >
                                                {this.state.files.toString()}
                                            </span>
                                        </label>
                                    </div>

                                </article>
                            </div>
                            <div className="tile is-parent">
                                <article className="tile is-child notification">
                                    {/* Handles the drag&drop area */}
                                    <DropZone handleDrop={this.onDrop} text={this.state.dropText} />
                                </article>
                            </div>

                        </div>
                        <div className="tile is-parent">
                            <div className="tile is-child">
                                <div className="field has-addons">
                                    <button type="submit" className="button is-grey" >
                                        <span className="file-icon">
                                            <FontAwesomeIcon icon='upload' />
                                        </span>
                                        <span>Upload</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
                {/* "Start simulation" button, active if the posting of the files went ok */}
                <div className="tile">
                    <button className="button" id="start-sim-ml-button" disabled={!this.state.loaded} onClick={this.onStartML}>
                        Simulation with Clustering only</button>
                    <button className="button" id="start-sim-dl-button" disabled={!this.state.loaded} onClick={this.onStartDL}>
                        Simulation with Deep Learning only</button>
                    <button className="button" id="start-sim-button" disabled={!this.state.loaded} onClick={this.onStart}>
                        Simulation with both techniques</button>
                </div>
                <div className="tile">
                    <button onClick={this.reset}>Reset</button>
                </div>
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