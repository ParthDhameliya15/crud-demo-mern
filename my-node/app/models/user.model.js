const mongoose = require('mongoose');

const UserSchema = mongoose.Schema({
       fullName: String,
        middleName: String,
        lastName: String,
        mobileNo: String,
        gender: String,
        country: String,
        hobby: Array
},{
    timestamp:true
});

module.exports = mongoose.model('User',UserSchema);