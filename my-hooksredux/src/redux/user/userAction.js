import {USER_DETAILS} from './userType'
import {USER_DELETE} from "./userType";
import {USER_UPDATE} from "./userType";
import {USER_EDIT} from "./userType";

export const userDetails = (data)=>{
        return {
            type:USER_DETAILS,
            payload: data
        }
};

export const userDelete = (data)=>{
        return{
            type:USER_DELETE,
            payload:data
        }
};

export const userEdit = (data)=>{
        return{
            type:USER_EDIT,
            payload:data
    }
};

export const userUpdate = (data,i)=>{
    return{
        index:i,
        type:USER_UPDATE,
        payload:data
    }
};