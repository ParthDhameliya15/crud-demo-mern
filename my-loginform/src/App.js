import './App.css';
import {Form, Input, Button, Checkbox, message} from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import 'antd/dist/antd.css';
import { Card } from 'antd';
import {useState} from "react";
import axios from "axios";

const App = (props) => {

 const[dynamic,setDynamic]=useState({});
 const[error,setError]=useState("User Login");

 const mySignUp = () =>{
     props.history.push({  pathname: '/SignUp'});
 };

 const handleOnChange = (e) =>{
     setDynamic({...dynamic,[e.target.name]:e.target.value})
 };

 const forgotPass = () =>{debugger
     props.history.push({  pathname: '/resetpassword'});
 };

 const mySubmit = () =>{
     axios.post('http://localhost:6001/users/match',dynamic)
         .then(res=>{
             if(res.data && res.data.details && res.data.details._id){
                 localStorage.setItem("token", JSON.stringify(res.data.token));
                 message.success("successfully Login");
                 props.history.push({pathname: '/loginUserTable'})
             }
             else{
                 message.error("Incorrect Login")
             }
         })
         .catch(err=>{
             console.log("Error")
         });
 };

 return (
     <Card className="CardCss" title={error} style={{marginLeft:350,marginRight:350,marginTop:50,marginBottom:0,backgroundColor:"#494A43"}}>
     <div className="formCss">
         <Form name="normal_login" className="login-form" initialValues={{ remember: true}}>

             <Form.Item name="emailAddress" rules={[{ required: true, message: 'Please input your Email Address!' }]}>
                 <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="Email Address"
                        value={dynamic.lEmailAddress} name="lEmailAddress" onChange={handleOnChange}/>
             </Form.Item>

             <Form.Item name="password" rules={[{ required: true, message: 'Please input your Password!' }]}>
                 <Input prefix={<LockOutlined className="site-form-item-icon" />} type="password"
                     placeholder="Password" value={dynamic.lPassword} name="lPassword" onChange={handleOnChange}/>
             </Form.Item>

             <Form.Item>
                 <Form.Item name="remember" valuePropName="checked" noStyle>
                     <Checkbox>Remember me</Checkbox>
                 </Form.Item>

                 <a className="login-form-forgot" onClick={forgotPass} href="">Forgot password</a>
             </Form.Item>

             <Form.Item>
                 <span style={{marginLeft:300}}>
                       <Button type="primary" htmlType="submit" onClick={mySubmit} className="login-form-button"> Log in </Button>
                 </span>
                 <span style={{marginLeft:20}}>
                     <Button type="primary" htmlType="submit" initialValues={{ remember: false}} onClick={mySignUp} className="login-form-button"> Sign Up </Button>
                 </span>
             </Form.Item>

         </Form>
     </div>
     </Card>

 );
};

export default App;


