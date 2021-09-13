import React, {useState,useEffect} from 'react';
import axios from "axios"

 const Body = (props) => {
        const[datas,setdatas]=useState([]);
        const[duplicate,setduplicate]=useState([]);
        const[searchValue,setsearchValue]=useState("");

    useEffect(()=>{
        getData()
    },[]);

    const getData = () => {
        axios.get("http://localhost:5000/users/get")
            .then(res => {
                setdatas(res.data);
                setduplicate(res.data)
            })
            .catch(err => {
                console.log("error")
            })
    };

    const myEdit =(id) => {
        props.history.push(`/edit/${id}`)
    };

    const myDelete = (id) => {
        axios.put(`http://localhost:5000/users/delete/${id}`)
            .then(res => {
                if (res.data && res.data.success){
                    getData()
                }
                  console.log("deleted succefully", res)
            })
            .catch(err => {
                console.log(err)
            });
    };

    const BackToHome = () => {
        props.history.push("/");
    };

    const handleOnChange = (e) =>{
        setsearchValue(e.target.value);
    };

    const SearchSubmit = () => {debugger
        if (!searchValue) {
            setdatas(duplicate);
        } else {
            const searchData = duplicate.filter(value => {debugger
                return value.fullName.includes(searchValue)
            });
            setdatas(searchData);
        }

    };


        return(
            <>
                <input type="text" name="searchValue" className="formfiled" placeholder="your search fname"
                       onChange={handleOnChange}/>
                <button className="btn btn-primary"  onClick={SearchSubmit}>Search</button>
                <br/><br/>

                <table align="center" border=" border: 1px solid black" width="100%" className="table table-striped">
                    <thead>
                    <tr>
                        <th>First Name</th>
                        <th>Middle Name</th>
                        <th>Last Name</th>
                        <th>Mobile No.</th>
                        <th>Gender</th>
                        <th>Country</th>
                        <th>Hobby</th>
                        <th>Action</th>
                    </tr>
                    </thead>

                    <tbody>
                    <>{
                          Array.isArray(datas)  && datas.map((item,i) =>(
                                <tr>
                                    <td>{i+1}.{item.fullName}</td>
                                    <td>{item.middleName}</td>
                                    <td>{item.lastName}</td>
                                    <td>{item.mobileNo}</td>
                                    <td>{item.gender}</td>
                                    <td>{item.country}</td>
                                    <td>{item.hobby}</td>
                                    <td> <button onClick = {() => {myEdit(item._id)}} className="myEdit btn btn-dark mr-2">Edit</button>
                                        <button onClick= {() => {myDelete(item._id)}} className="myDelete  btn btn-dark ">Delete</button>
                                    </td>
                                </tr>
                            ))
                        }
                        {
                            <button onClick = {() => BackToHome()} className="myEdit btn btn-dark mr-2">Back To Home</button>
                        }

                    </>
                    </tbody>
                </table>
            </>
        )
};

export default Body;