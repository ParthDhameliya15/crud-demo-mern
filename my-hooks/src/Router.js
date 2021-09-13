import  React from 'react';
import {Switch,Route} from "react-router-dom";
import App from "./App";
import Body from "./body";

function Router(){
    return (
        <>
            <Switch>
                <Route exact={true} path="/" component={App}/>
                <Route path="/table" component={Body}/>
                <Route path="/edit/:id" component={App}/>
            </Switch>

        </>
    );

}

export default Router;