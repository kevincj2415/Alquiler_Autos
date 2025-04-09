const express = require("express");
const router = express.Router();
const { getCars } = require("../controllers/car.controller");

router.get("/", getCars);

module.exports = router;
