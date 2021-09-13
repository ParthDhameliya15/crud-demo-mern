import {USER_DETAILS} from './userType'
import {USER_UPDATE} from './userType'
import {USER_DELETE} from './userType'
import {USER_EDIT} from './userType'

const initialState={
        data:[],
        editUserData:{}
};

const userDetailsReducer=(state=initialState,action)=>{
    switch (action.type) {
        case USER_DETAILS:
            return{
                ...state,
                data: [...state.data,action.payload]
            };
        case USER_DELETE:{
            return {
                ...state,
                data: state.data.filter((data,i)=>i !== action.payload)
            }
        }
        case  USER_EDIT:{
            return {
                ...state,
                editUserData: state.data.find((data,i)=> i === action.payload) || {}
            }
        }
        case  USER_UPDATE:{
            return {
                ...state,
                data: [...action.payload]
            }
        }
        default:return initialState
    }
};

export default userDetailsReducer;