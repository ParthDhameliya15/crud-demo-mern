require("../models/user.model");
const express = require('express');
const router = express.Router();
const controllers = require('../controllers/user.controllers');

router.post('/create', controllers.create);
router.post('/match', controllers.match);
router.get('/get', controllers.get);
router.post('/forgot', controllers.forgot);
router.put('/passwordupdate/:id', controllers.passwordupdate);


module.exports = router;