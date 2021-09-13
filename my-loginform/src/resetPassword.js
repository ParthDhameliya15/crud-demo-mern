import './App.css';
import {Form, Input, Button,message} from 'antd';
import { UserOutlined } from '@ant-design/icons';
import 'antd/dist/antd.css';
import { Card } from 'antd';
import {useState} from "react";
import axios from "axios";

const ResetPassword = (props) => {

    const[dynamic,setDynamic]=useState({});

    const handleOnChange = (e) =>{
        setDynamic({...dynamic,[e.target.name]:e.target.value})
    };

    const ResetPass = () =>{
        axios.post('http://localhost:6001/users/forgot',dynamic)
            .then(res=>{console.log(res.data);
                if(res.data && res.data._id){
                    const id=res.data._id;
                    props.history.push({  pathname: `/renewpassword/${id}`});
                }else{
                    message.error("user not found")
                }
            })
            .catch(err=>{
                console.log("Error")
            });
    };


    return (
        <Card className="CardCss" title="Reset Password" style={{marginLeft:350,marginRight:350,marginTop:50,marginBottom:0,backgroundColor:"#494A43"}}>
            <div className="formCss">
                <Form name="normal_login" className="reset-form" initialValues={{ remember: true}}>

                    <Form.Item name="emailAddress" rules={[{ required: true, message: 'Please input your Email Address!' }]}>
                        <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="Email Address"
                               value={dynamic.rEmailAddress} name="rEmailAddress" onChange={handleOnChange}/>
                    </Form.Item>




                    <Form.Item>
                 <span style={{marginLeft:300}}>
                       <Button type="primary" htmlType="submit" onClick={ResetPass} className="reset-form-button">Submit</Button>
                 </span>
                    </Form.Item>

                </Form>
            </div>
        </Card>

    );
};

export default ResetPassword;


