import React,{useState,useEffect} from 'react'
import {Table, Button} from 'antd';
import axios from "axios";

const LoginUserTable = (props) =>{
        const[datas,setdatas]=useState([]);

        const mySubmit = () =>{
            props.history.push({  pathname: '/'});
            localStorage.removeItem("token");
        };

        useEffect(()=>{
                axios.get('http://localhost:6001/users/get')
                    .then(res => {
                        setdatas(res.data);
                    })
                    .catch(err => {
                            console.log("error")
                    })
        });


        const columns = [
                {title: 'username', dataIndex: 'username', key: 'username', render: text => <a>{text}</a>,},
                {title: 'emailAddress', dataIndex: 'emailAddress', key: 'emailAddress',},
                {title: 'password', dataIndex: 'password', key: 'password',},
                ];

        return(
            <div style={{width:1000,marginLeft:150}}>
                <Button type="primary" htmlType="submit" onClick={mySubmit} className="login-form-button"> Log Out </Button>
                    <Table columns={columns} dataSource={datas} />
            </div>
        )
};

export  default  LoginUserTable;

