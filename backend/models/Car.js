const mongoose = require('mongoose');

const autoSchema = new mongoose.Schema({
  marca: String,
  modelo: String,
  año: Number,
  precioPorDia: Number,
  available: Boolean
});

const Auto = mongoose.model('Auto', autoSchema);

module.exports = Auto;
