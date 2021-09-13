import React from 'react'
import { Redirect, Route } from 'react-router-dom'

const PrivateRoute = ({ component: Component, ...rest }) => {

    const isLoggedIn= JSON.parse(localStorage.getItem('token'));

    return (
        <Route
            {...rest}
            render={props =>
                isLoggedIn ? (
                    <Component {...props} />
                ) : (
                    <Redirect to={{ pathname: '/' }} />
                )
            }
        />
    )

};
export default PrivateRoute;
