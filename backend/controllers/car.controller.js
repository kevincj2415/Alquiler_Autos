const Car = require("../models/Car");

exports.getCars = async (req, res) => {
  const cars = await Car.find({ available: true });
  res.json(cars);
};
