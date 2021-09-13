const User = require('../models/user.model');

    exports.create = function (req, res) {
    let user = new User(
        {
            fullName: req.body.fullName,
            middleName: req.body.middleName,
            lastName: req.body.lastName,
            mobileNo: req.body.mobileNo,
            gender: req.body.gender,
            country: req.body.country,
            hobby: req.body.hobby,

        }
    );

    user.save(function (myData,err) {
       try{
           return res.status(200).send({success: true})
       }
       catch (e) {
           return res.status(401).send("somethigs went wrong")
       }
    })
};

exports.get = async ( req, res ) => {
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

exports.getById = async ( req, res ) => {
    try {

        const details = await User.findOne({_id : req.params.id});
        if(details && details._id){
            res.send(details);
        }else {
            res.send("No Record Found");
        }

    } catch ( err ) {
        res.send( err );
    }
};

exports.update = async ( req, res ) => {
    try {
         const details = await User.findByIdAndUpdate({_id : req.params.id}, req.body);
         console.log(req.body);
         if(details && details._id){
            res.send(details);
        }else {
            res.send("No Record Found");
        }

    } catch ( err ) {
        res.send( err );
    }
};

exports.delete = async ( req, res ) => {
    try {
       await User.remove({_id : req.params.id});
       res.send({success:true})

    } catch ( err ) {
        res.send( err );
    }
};