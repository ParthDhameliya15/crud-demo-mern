const mongoose = require('mongoose');

const UserSchema = mongoose.Schema({
    username: String,
    emailAddress: String,
    password: String,
    confirmPassword: String,

},{
    timestamp:true
});

module.exports = mongoose.model('User',UserSchema);