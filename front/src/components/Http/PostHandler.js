import React, { Component } from "react";
import axios from "axios";
import DropZone from "./Drag&Drop";
import './PostHandler.css';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

class HttpRequestHandler extends Component {

    constructor(props) {
        super(props);
        this.state = {
            files: [],
            fileNames : {},
            loaded : false, // Contains all the uploaded files
            dropText : "Drop your files here !"
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
                        this.setState({loaded : true});
                    })
            }
        })
    }
    onChange(e) { // When entering files with input ()
        for(let f of e.target.files) {
            if(!this.state.fileNames[f.name]) {
                let dic = JSON.parse(JSON.stringify(this.state.fileNames));
                dic[f.name] = 1;
                let array = this.state.files;
                array.push(f);
                this.setState({files : array, fileNames : dic});
            }
        }
    }

    onStart(e) { // Start simulation button
        axios.get("http://localhost:8000/startsimulation")
            .then((res) => console.log("Simulation started !"));
    }

    fileUpload(files) {
        const url = 'http://localhost:8000/upload'; // server route to POST request
        const formData = new FormData();
        let i = 0;
        console.log(files);
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

    onDrop(file, e) {
        if(file) {
            for(let f of file) {
                if(!this.state.fileNames[f.name]) {
                    let dic = JSON.parse(JSON.stringify(this.state.fileNames));
                    dic[f.name] = 1;
                    let text = "" + Object.keys(dic).length + " files dropped.";
                    console.log(dic);
                    let array = this.state.files;
                    array.push(f);
                    this.setState({files : array, dropText : text, fileNames : dic});
                }
            }
        }
    }

    render() {
        return (
            <div>
            <form onSubmit={this.onFormSubmit} className="container">
                <p>
                    <strong className="has-text-white-ter">Upload your .PRP files</strong>
                </p>
                <div class="file has-name is-boxed is-centered is-fullwidth" >
                {/* CSS !! */}
                    <DropZone handleDrop = {this.onDrop} text = {this.state.dropText}/> 
                    {/* CSS !! */}
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
            {/* CSS !! */}
            <button class="button" disabled={!this.state.loaded} onClick = {this.onStart}>
            Start simulation</button>
            {/* CSS !! */}
            </div>

        )
    }
}

export default HttpRequestHandler;