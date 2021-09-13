import  React from 'react';
import {Switch,Route} from "react-router-dom";
import PrivateRoute from "../src/privateRoute"
import App from "./App";
import SignUp from "./SignUp";
import LoginUserTable from "./loginUserTable"
import ResetPassword from "./resetPassword";
import ReNewPassword from "./renewPassword";


function Router(){
    return (
        <>
            <Switch>
                <Route exact={true} path="/" component={App}/>
                <Route path="/SignUp" component={SignUp}/>
                <Route path="/resetpassword" component={ResetPassword}/>
                <Route path="/renewpassword/:id" component={ReNewPassword}/>
                <PrivateRoute path="/loginUserTable" component={LoginUserTable}/>
            </Switch>

        </>
    );

}

export default Router;