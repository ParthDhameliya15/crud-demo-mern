import  React,{useState} from 'react';
import {Button, Card, Form, Input} from 'antd'
import {LockOutlined } from '@ant-design/icons';
import 'antd/dist/antd.css';
import axios from 'axios';


const ReNewPassword=(props)=>{

    const[dynamic,setDynamic]=useState({});

    const myLogin = () =>{
        props.history.push({pathname: '/'});
    };

    const handleOnChange = (e) =>{
        setDynamic({...dynamic,[e.target.name]:e.target.value})
    };

    const mySubmit = () =>{debugger
        const password=dynamic.nPassword;
        const confirmPassword=dynamic.nConfirmPassword;
        const id = props.match && props.match.params && props.match.params.id;
        console.log("11", password)
        if (id){
            if(password===confirmPassword){
                axios.put(`http://localhost:6001/users/passwordupdate/${id}`,{password:password})
                    .then(res=>{debugger
                        localStorage.setItem("token", JSON.stringify(res.data.token));
                        console.log("data successfully added")
                    })
                    .catch(err=>{
                        console.log("Error")
                    });

                props.history.push({pathname:'/'})
            }
        }


    };

    return(
        <>
            <Card className="CardCss" title={<span><h3>Set New Password</h3><br/></span>}
                  style={{marginLeft:350,marginRight:350,marginTop:50,marginBottom:0,backgroundColor:"#494A43"}}>
                <div className="formCss">

                    <Form name="normal_login" className="newPass-form">

                        <Form.Item name="password" rules={[{ required: true, message: 'Please input your New Password!' }]}>
                            <Input prefix={<LockOutlined className="site-form-item-icon" />} name="nPassword" type="password"
                                   placeholder="New Password" onChange={handleOnChange} value=""/>
                        </Form.Item>

                        <Form.Item name="confirmPassword" rules={[{ required: true, message: 'Please input your Password!' }]}>
                            <Input prefix={<LockOutlined className="site-form-item-icon" />} name="nConfirmPassword" type="password"
                                   placeholder="Confirm Password" onChange={handleOnChange}/>
                        </Form.Item>

                        <Form.Item>

                            <span style={{marginLeft:20}}>
                                    <Button type="primary" htmlType="submit" initialValues={{ remember: false}} onClick={mySubmit}
                                            className="newPassword-form-button"> Submit</Button>
                            </span>
                        </Form.Item>

                    </Form>
                </div>
            </Card>
            <div className="text-center">Password does not send? <button onClick={myLogin}>Click here</button></div>
        </>
    )
};
export default ReNewPassword;