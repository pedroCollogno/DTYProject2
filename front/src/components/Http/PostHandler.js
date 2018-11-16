import React, { Component } from "react";
import axios from "axios";
import DropZone from "./Drag&Drop";
import './PostHandler.css';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

class HttpRequestHandler extends Component {

    constructor(props) {
        super(props);
        this.state = {
            files: {},
            loaded: false // Contains all the uploaded files
        };
        this.onFormSubmit = this.onFormSubmit.bind(this);
        this.onChange = this.onChange.bind(this);
        this.fileUpload = this.fileUpload.bind(this);
        this.onDrop = this.onDrop.bind(this);
    }
    onFormSubmit(e) {
        e.preventDefault() // Stop form submit
        this.fileUpload(this.state.files).then((response) => {
            console.log(response.data); // Should be "POST ok !"
            if (response.data === "POST ok !") {
                axios.get("http://localhost:8000/getstations")
                    .then((response) => {
                        this.props.getStations(response);
                        this.setState({ loaded: true });
                    })
            }
        })
    }
    onChange(e) { // When entering files with input ()
        for (let f of e.target.files) {
            if (!this.state.files[f.name]) {
                let dic = JSON.parse(JSON.stringify(this.state.files));
                dic[f.name] = f;
                this.setState({ files: dic });
            }
        }
        this.setState({ files: e.target.files });
    }

    onStart(e) { // Start simulation button
        axios.get("http://localhost:8000/startsimulation")
            .then((res) => console.log("Simulation started !"));
    }

    fileUpload(files) {
        const url = 'http://localhost:8000/upload'; // server route to POST request
        const formData = new FormData();
        let i = 0;
        for (let fileName of Object.keys(files)) {
            formData.append("File" + i, files[fileName], fileName); // standardized name for formData entry : "File{i}"
            i += 1;
        }
        const config = {
            headers: {
                'content-type': 'multipart/form-data'
            }
        }
        return axios.post(url, formData, config) // sends POST request
    }

    onDrop(file, e) {
        if (file) {
            for (let f of file) {
                if (!this.state.files[f.name]) {
                    let dic = JSON.parse(JSON.stringify(this.state.files));
                    dic[f.name] = f;
                    this.setState({ files: dic });
                }
            }
        }
    }

    render() {
        return (
            <div>
                <p>
                    <strong className="has-text-white-ter">Upload your .PRP files</strong>
                </p>
                <form onSubmit={this.onFormSubmit}>

                    <div className="tile is-ancestor is-vertical">
                        <div className="tile">

                            <div className="tile is-parent" >
                                <article className="tile is-child notification is-warning">
                                    <div className="file has-name is-boxed is-centered is-fullwidth" >

                                        <label className="file-label" >
                                            <input type="file" className="file-input" multiple onChange={this.onChange} />
                                            <span className="file-cta">
                                                <span className="file-icon">
                                                    <FontAwesomeIcon icon='download' />
                                                </span>
                                                <span className="file-label">Choose a .PRP file…</span>
                                            </span>
                                            <span className="file-name has-text-white-ter" >
                                                {this.state.files.toString()}
                                            </span>
                                        </label>
                                    </div>

                                </article>
                            </div>
                            <div className="tile is-parent">
                                <article className="tile is-child notification is-warning">
                                    <DropZone handleDrop={this.onDrop} />
                                </article>
                            </div>

                        </div>
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
                </form>

                {/* CSS !! */}
                <button className="button" disabled={!this.state.loaded} onClick={this.onStart}>
                    Start simulation</button>
                {/* CSS !! */}
            </div>

        )
    }
}

export default HttpRequestHandler;