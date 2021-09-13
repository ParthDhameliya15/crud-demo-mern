const redux = require('redux');
const createStore = redux.createStore;
const applyMiddleware = redux.applyMiddleware;
const thunkmiddleware = require('redux-thunk').default;
const axios = require('axios');

const initialState = {
    loading: false,
    users: [],
    error: ''
};

const user_request = "user_request";
const user_success = "user_success";
const user_error = "user_error";

const userRequest = () => {
    return {
        type: user_request,
    }
};

const userSuccess = (users) => {
    return {
        type: user_success,
        payload: users
    }
};

const userError = (error) => {
    return {
        type: user_error,
        payload: error
    }
};

const reducer = (state = initialState, action) => {
    switch (action.type) {
        case ("user_request"):
            return {
                ...state, loading: true
            };
        case ("user_success"):
            return {
                loading: false, users: action.payload, error: ''
            };
        case ("user_error"):
            return {
                loading: false, users: [], error: action.payload
            };
    }
};

const fetchUser = () => {
    return function (dispatch) {
        dispatch(userRequest());
        axios.get("https://jsonplaceholder.typicode.com/users/")
            .then(res => {
                const users = res.data.map(user => user.name);
                dispatch(userSuccess(users))
            })
            .catch(err => {
                dispatch(userError(err.message))
            })
    }
};

const store = createStore(reducer, applyMiddleware(thunkmiddleware));
store.subscribe(() => {
    console.log(store.getState())
});
store.dispatch(fetchUser());