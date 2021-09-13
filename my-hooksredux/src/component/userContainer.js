import React, {useState, useEffect} from 'react';
import {Link} from "react-router-dom";
import axios from "axios"
import "../App.css"
import {userDetails} from "../redux";
import {connect} from "react-redux";
import {userEdit, userUpdate} from "../redux/user/userAction";


const hobyys = ["football", "carrom", "basketball", "chess"];

const UserContainer = (props) => {
    const {editUserData} = props;
    const [dynamic, setdynamic] = useState(editUserData || {});
    const [title, settitle] = useState("crude in React");
    const [datas, setdatas] = useState([]);
    const [hobby, sethobby] = useState([]);
    const [isIndex, setisIndex] = useState("");
    const [searchValue, setsearchValue] = useState("");
    const [errors, seterrors] = useState({});
    const [duplicate, setduplicate] = useState([]);

    useEffect(async () => {
        await getData()
    }, []);

    const getData = () => {
        axios.get("http://localhost:5000/users/get")
            .then(res =>
                console.log("hiii", res)
            )
            .catch(err =>
                console.log("err", err))
    };

    const handleOnChange = (e) => {
        if (e.target.name === "hobby") {
            debugger
            let value = e.target.value;
            if (e.target.checked) {
                sethobby((prev) => [...prev, value]);
            } else {
                sethobby(hobby.filter(v => v !== value))
                // sethobby(hobby);
            }
            console.log(hobby)
        } else {
            setdynamic({...dynamic, [e.target.name]: e.target.value});
        }
    };

    const validation = (name, value) => {
        const numRegx = /^[0-9\b]+$/;
        switch (name) {
            case ("fullName"):
                if (!value) {
                    return "fullName is required"
                } else {
                    return ""
                }
            case ("middleName"):
                if (!value) {
                    return "middal name is required"
                } else {
                    return ""
                }
            case ("lastName"):
                if (!value) {
                    return "Last name is required"
                } else {
                    return ""
                }
            case ("mobileNo"):
                if (!numRegx.test(value)) {
                    return "mobileNo is required"
                } else {
                    return ""
                }
            case ("gender"):
                if (!value) {
                    return "gender is required"
                } else {
                    return ""
                }
            case ("country"):
                if (!value) {
                    return "country is required"
                } else {
                    return ""
                }
        }
    };

    const Table = () => {
        props.history.push("/table");
    };

    const mySubmit = () => {
        let errors = {};
        const data = {
            fullName: dynamic.fullName,
            middleName: dynamic.middleName,
            lastName: dynamic.lastName,
            mobileNo: dynamic.mobileNo,
            gender: dynamic.gender,
            country: dynamic.country,
            hobby: hobby
        };
        Object.keys(data).forEach(key => {
            const error = validation(key, data[key]);
            if (error && error.length > 0) {
                errors[key] = error;
            }
        });
        if (Object.keys(errors).length > 0) {
            seterrors(errors);
            return
        }
        console.log("index", isIndex);
        if (isIndex === "") {
            debugger
            setdatas([...datas, data]);
            setduplicate([...datas, data]);

            dynamic.hobby = hobby;
            console.log("1", dynamic);
            props.dispatch(userDetails(dynamic));
            axios.post('http://localhost:5000/users/create', dynamic).then(res => {
                console.log("data passed successfully");
            })
                .catch(err => {
                    console.log("error")
                })
        } else {
            debugger
            dynamic.hobby = hobby;
            props.list[isIndex] = data;
            props.dispatch(userUpdate(props.list, isIndex));
            console.log("2", dynamic)
        }
        resetform();

    };

    useEffect(() => {
        resetform();
        const id = props.match && props.match.params && props.match.params.id;
        if (id) {
            setisIndex(parseInt(id));
            props.dispatch(userEdit(parseInt(id)));
        }
    }, []);

    useEffect(() => {
        debugger
        setdynamic(props.editUserData);
        console.log("111111", props.editUserData);
        props.editUserData && props.editUserData.hobby && sethobby(props.editUserData.hobby);
    }, [props.editUserData]);

    const resetform = () => {
        setdynamic({});
        sethobby([]);
        seterrors("");
        setisIndex("");
    };

    return (
        <div className={"App"} style={{margin: 10, marginLeft: 480}}>
            {title}<br/>
            <div className="input-group col-md-6">
                <span> <label>First Name:</label></span>
                <span className="glyphicon glyphicon-user input-group-text" style={{marginLeft: 25}}/>
                <input type="text" className=" formfiled" name="fullName" value={dynamic.fullName}
                       placeholder="Enter Your First Name"
                       onChange={handleOnChange}/>
                <span style={{color: "red"}}>{errors && errors.fullName}</span><br/><br/>
            </div>
            <div className="input-group col-md-6">
                <span> <label>Middle name:</label></span>
                <span className="glyphicon glyphicon-user input-group-text" style={{marginLeft: 9}}/>
                <input type="text" className=" formfiled" name="middleName" value={dynamic.middleName}
                       placeholder="Enter Your Middle Name"
                       onChange={handleOnChange}/>
                <span style={{color: "red"}}>{errors && errors.middleName}</span><br/><br/>
            </div>
            <div className="input-group col-md-6">
                <span> <label>Last name:</label></span>
                <span className="glyphicon glyphicon-user input-group-text" style={{marginLeft: 32}}/>
                <input type="text" className=" formfiled" name="lastName" value={dynamic.lastName}
                       placeholder="Enter Your Last Name"
                       onChange={handleOnChange}/>
                <span style={{color: "red"}}>{errors && errors.lastName}</span><br/><br/>
            </div>
            <div className="input-group col-md-6">
                <span> <label>Mobile No:</label></span>
                <span className="glyphicon glyphicon-user input-group-text" style={{marginLeft: 31}}/>
                <input type="tel" className=" formfiled" name="mobileNo" value={dynamic.mobileNo}
                       placeholder="Enter Your Mobile Number"
                       onChange={handleOnChange}/>
                <span style={{color: "red"}}>{errors && errors.mobileNo}</span><br/><br/>
            </div>

            <div className="center"><h3>*select your gender</h3></div>

            <div className="form-check">
            <span style={{marginRight: 18}}> <input className="form-check-input mr-3" type="radio" name="gender"
                                                    value="male"
                                                    checked={dynamic.gender === "male"} id="male"
                                                    onChange={handleOnChange}/></span>
                <span><label className="form-check-label mr-3"> Male </label></span>
            </div>
            <div className="form-check">
            <span style={{marginRight: 18}}> <input className="form-check-input mr-3" type="radio" name="gender"
                                                    value="female"
                                                    checked={dynamic.gender === "female"} id="female"
                                                    onChange={handleOnChange}/></span>
                <span><label className="form-check-label mr-3"> Female </label></span>
            </div>
            <div className="form-check">
            <span style={{marginRight: 18}}> <input className="form-check-input mr-3" type="radio" name="gender"
                                                    value="other"
                                                    checked={dynamic.gender === "other"} id="other"
                                                    onChange={handleOnChange}/></span>
                <span><label className="form-check-label mr-3"> Other </label></span>
            </div>
            <span style={{color: "red"}}>{errors && errors.gender}</span>
            <br/>


            <h3 className=" ">*select your country</h3>
            <div className=" ">
                <label htmlFor="country">Choose a country:</label>
                <select name="country" id="country" onChange={handleOnChange}>
                    <option value="" selected={dynamic.country === ""}>select country</option>
                    <option value="India" selected={dynamic.country === "India"}>India</option>
                    <option value="America" selected={dynamic.country === "America"}>America</option>
                    <option value="Russia" selected={dynamic.country === "Russia"}>Russia</option>
                    <option value="Canada" selected={dynamic.country === "Canada"}>Canada</option>
                </select>
                <span style={{color: "red"}}>{errors && errors.country}</span><br/><br/>
            </div>

            <br/>

            <h3>Hobby:</h3>
            {
                hobyys.map(value => (
                        <div className="custom-control custom-checkbox">
                            <input type="checkbox" name="hobby" value={value}
                                   checked={hobby.includes(value)} onChange={handleOnChange}/>
                            <label htmlFor={value}>{value}</label><br/>
                        </div>
                    )
                )
            }

            <br/><br/>
            <Link to="/table">Table</Link>
            <button className="btn btn-primary" onClick={mySubmit}>Submit</button>

            <button className="btn btn-dark" onClick={Table}>Show Table</button>

            <br/><br/>

        </div>
    )

};

const mapStateToProps = (state) => {
    console.log(state);
    return {
        list: state.data,
        editUserData: state.editUserData
    }
};

export default connect(mapStateToProps)(UserContainer);
