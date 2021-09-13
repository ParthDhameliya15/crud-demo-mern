import  React,{useState} from 'react';
import {Button, Card, Checkbox, Form, Input} from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import 'antd/dist/antd.css';
import axios from 'axios';


const SignUp=(props)=>{

    const[dynamic,setDynamic]=useState({});

    const myLogin = () =>{
            props.history.push({pathname: '/'});
    };

    const handleOnChange = (e) =>{
            setDynamic({...dynamic,[e.target.name]:e.target.value})
    };

    const mySubmit = () =>{
        const password=dynamic.password;
        const confirmPassword=dynamic.confirmPassword;

            if(password===confirmPassword){
                axios.post('http://localhost:6001/users/create',dynamic)
                    .then(res=>{debugger
                        localStorage.setItem("token", JSON.stringify(res.data.token));
                        console.log("data successfully added")
                    })
                    .catch(err=>{
                        console.log("Error")
                    });

                props.history.push({pathname:'/'})
            }
    };

    return(
        <>
            <Card className="CardCss" title={<span><h3>Sign Up</h3><br/><h5>Please fill in this form to create an account!</h5></span>}
                  style={{marginLeft:350,marginRight:350,marginTop:50,marginBottom:0,backgroundColor:"#494A43"}}>
                <div className="formCss">

                    <Form name="normal_login" className="login-form">
                        <Form.Item name="username" rules={[{ required: true, message: 'Please input your Username!' }]}>
                            <Input prefix={<UserOutlined className="site-form-item-icon" />} name="username" type="text" value=""
                                   onChange={handleOnChange} placeholder="Username" />
                        </Form.Item>

                        <Form.Item name="emailAddress" rules={[{ required: true, message: 'Please input your Email Address!' }]}>
                            <Input prefix={<UserOutlined className="site-form-item-icon" />} name="emailAddress" type="email" value=""
                                    onChange={handleOnChange} placeholder="Email Address" />
                        </Form.Item>

                        <Form.Item name="password" rules={[{ required: true, message: 'Please input your Password!' }]}>
                            <Input prefix={<LockOutlined className="site-form-item-icon" />} name="password" type="password"
                                   placeholder="Password" onChange={handleOnChange} value=""/>
                        </Form.Item>

                        <Form.Item name="confirmPassword" rules={[{ required: true, message: 'Please input your Password!' }]}>
                            <Input prefix={<LockOutlined className="site-form-item-icon" />} name="confirmPassword" type="password"
                                   placeholder="Confirm Password" onChange={handleOnChange}/>
                        </Form.Item>

                        <Form.Item>
                            <Form.Item name="acceptPrivacy" valuePropName="checked" noStyle>
                                <Checkbox>I accept the Terms of Use & Privacy Policy</Checkbox>
                            </Form.Item>

                            <a className="login-form-forgot" href="">
                                Forgot password
                            </a>
                        </Form.Item>

                        <Form.Item>

                            <span style={{marginLeft:20}}>
                                    <Button type="primary" htmlType="submit" initialValues={{ remember: false}} onClick={mySubmit}
                                            className="login-form-button"> Sign Up </Button>
                            </span>
                        </Form.Item>

                    </Form>
                </div>
            </Card>
            <div className="text-center">Already have an account? <button onClick={myLogin}>Login here</button></div>
        </>
        )
};
export default SignUp;