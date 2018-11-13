import React, { Component } from "react";
import axios from "axios";
import './PostHandler.css';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

class HttpRequestHandler extends Component {

    constructor(props) {
        super(props); // TODO : get props from Drag&Drop Component
        this.state = {
            files: {} // Contains all the uploaded files
        };
        this.onFormSubmit = this.onFormSubmit.bind(this);
        this.onChange = this.onChange.bind(this);
        this.fileUpload = this.fileUpload.bind(this);
    }
    onFormSubmit(e) {
        e.preventDefault() // Stop form submit
        this.fileUpload(this.state.files).then((response) => {
            console.log(response.data); // Should be "POST ok !"
            if (response.data === "POST ok !") {
                axios.get("http://localhost:8000/getstations")
                    .then((response) => {
                        this.props.getStations(response);
                        axios.get("http://localhost:8000/startsimulation")
                            .then((res) => console.log("Simulation started !"))
                    })
            }
        })
    }
    onChange(e) {
        this.setState({ files: e.target.files });
    }
    fileUpload(files) {
        const url = 'http://localhost:8000/upload'; // server route to POST request
        const formData = new FormData();
        let i = 0;
        for (let file of files) {
            formData.append("File" + i, file, file.name); // standardized name for formData entry : "File{i}"
            i += 1;
        }
        const config = {
            headers: {
                'content-type': 'multipart/form-data'
            }
        }
        return axios.post(url, formData, config) // sends POST request
    }

    render() { // temporary form
        return (
            <form onSubmit={this.onFormSubmit} className="container">
                <p>
                    <strong className="has-text-white-ter">Upload your .PRP files</strong>
                </p>
                <div class="file has-name is-boxed is-centered is-fullwidth" >
                    <label class="file-label" >
                        <input type="file" className="file-input" multiple onChange={this.onChange} />
                        <span class="file-cta">
                            <span class="file-icon">
                                <FontAwesomeIcon icon='download' />
                            </span>
                            <span class="file-label">Choose a .PRP file…</span>
                        </span>
                        <span class="file-name has-text-white-ter" >
                            {this.state.files.toString()}
                        </span>
                    </label>
                </div>
                <div class="field has-addons">
                    <button type="submit" className="button is-grey" >
                        <span class="file-icon">
                            <FontAwesomeIcon icon='upload' />
                        </span>
                        <span>Upload</span>
                    </button>
                </div>
            </form>
        )
    }
}

export default HttpRequestHandler;