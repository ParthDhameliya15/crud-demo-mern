import userDetailsReducer from "./user/userReducer";
import {createStore} from "redux";

const store=createStore(userDetailsReducer,window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__());

export default store;