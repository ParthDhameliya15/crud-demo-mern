const User = require('../models/user.model');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const config = require('../../config');
const nodemailer = require('nodemailer');


exports.create = function (req, res) {
    const reqbodypassword = bcrypt.hashSync(req.body.password, 8);
    let user = new User(
        {
            username: req.body.username,
            emailAddress: req.body.emailAddress,
            password: reqbodypassword,
            confirmPassword: req.body.confirmPassword,
        }
    );

    user.save(function (myData,user) {
        try{
            return res.status(200).send("Successfully created")
        }
        catch (e) {
            return res.status(401).send("somethigs went wrong")
        }
    })
};

exports.match = async (req, res) => {
    try {
        const details = await User.findOne({emailAddress: req.body.lEmailAddress});
        if (details && details._id) {
            const token = jwt.sign({ id: details._id }, config.secret, {
                expiresIn: 86400
            });
            const passwordIsValid = bcrypt.compareSync( req.body.lPassword,details.password);
            if (passwordIsValid) {
                res.send({token,details});
            } else {
                res.send("Please enter a valid login");
            }
        }
    } catch {
        (err);
        {
            res.send(err);
        }
    }
};

exports.get =async (req,res) =>  {
    try {
        const details = await User.find({});
        if(details.length){
            res.send(details);
        }else {
            res.send("No Record Found");
        }

    } catch ( err ) {
        res.send( err );
    }
};

exports.forgot =async (req,res) =>  {
    try {
        const details = await User.findOne({emailAddress: req.body.rEmailAddress});
        console.log(details);
        if (details && details._id){
            let transporter = nodemailer.createTransport({
                host: "smtp.gmail.com",
                port: 587,
                secure: false,
                requireTLS:true,
                auth: {
                    user: "parthdhameliya266@gmail.com",
                    pass: "parth.patel",
                },
            });
            let mailOptions={
                from: "parthdhameliya266@gmail.com",
                to: req.body.rEmailAddress, // list of receivers
                subject: "Hello ✔", // Subject line
                text: "Hello world?", // plain text body
                html: `<b>{http://localhost:3000/renewpassword/${details._id}}</b>`, // html body
            };
            transporter.sendMail(mailOptions,function (error,info) {
                if(error){
                    console.log(error);
                }
                else{
                    console.log("email has been sent",info.response);
                    res.send(details);
                }
            })
        }else {
            res.send("No Record Found");
        }

    }catch ( err ) {
        res.send( err );
    }
};

exports.passwordupdate=async (req,res)=>{
    try {
        console.log("req.body.password",req.body);
        const reqbodypassword = bcrypt.hashSync(req.body.password, 8);
        const details = await User.findByIdAndUpdate({_id : req.params.id}, {password: reqbodypassword});
        if(details && details._id){
            res.send(details);
        }else {
            res.send("No Record Found");
        }

    } catch ( err ) {
        res.send( err );
    }
};
