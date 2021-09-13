require("../models/user.model");
const express = require('express');
const router = express.Router();
const controllers = require('../controllers/user.controllers');

router.post('/create', controllers.create);
router.get('/get',controllers.get);
router.get('/:id',controllers.getById);
router.put('/:id',controllers.update);
router.put('/delete/:id',controllers.delete);

 module.exports = router;