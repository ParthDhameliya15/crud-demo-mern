import  React, {Component} from 'react';
import {Switch,Route} from "react-router-dom";
import App from "./App";
import UserBody from "./component/userBody";
import store from "./redux/store";
import {Provider} from "react-redux";

const Router = () => {
    return (
        <Provider store={store}>
            <Switch>
                <Route exact={true} path="/" component={App}/>
                <Route path="/table" component={UserBody}/>
                <Route path="/edit/:id" component={App}/>
            </Switch>
        </Provider>
    );

};

export default Router;