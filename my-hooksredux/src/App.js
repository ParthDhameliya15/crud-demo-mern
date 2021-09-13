import React from 'react';
import UserContainer from "./component/userContainer";

const App = (props) => {
    return (
        <>
            <UserContainer {...props}/>
        </>

    );
};

export default App;