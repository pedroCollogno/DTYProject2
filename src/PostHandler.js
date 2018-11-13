import React, {Component} from "react";
import axios from "axios";

class HttpRequestHandler extends Component {

    constructor(props) {
        super(props); // TODO : get props from Drag&Drop Component
        this.state = {
            files:{} // Contains all the uploaded files
        };
        this.onFormSubmit = this.onFormSubmit.bind(this);
        this.onChange = this.onChange.bind(this);
        this.fileUpload = this.fileUpload.bind(this);
    }
    onFormSubmit(e){
        e.preventDefault() // Stop form submit
        this.fileUpload(this.state.files).then((response)=>{
            console.log(response.data); // Should be "POST ok !"
            if(response.data === "POST ok !") {
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
        this.setState({files: e.target.files});
    }
    fileUpload(files){
        const url = 'http://localhost:8000/upload'; // server route to POST request
        const formData = new FormData();
        let i = 0;
        for(let file of files){
            formData.append("File" + i,file, file.name); // standardized name for formData entry : "File{i}"
            i += 1;
        }
        const config = {
            headers: {
                'content-type': 'multipart/form-data'
            }
        }
        return  axios.post(url, formData,config) // sends POST request
    }
    
    render() { // temporary form
        return (
          <form onSubmit={this.onFormSubmit}>
            <h1>PRP Upload</h1>
            <input type="file" multiple onChange={this.onChange} />
            <button type="submit">Upload</button>
          </form>
       )
    }

}

export default HttpRequestHandler;