const mongoose = require("mongoose");
const BookingSchema = new mongoose.Schema({
  userId: mongoose.Schema.Types.ObjectId,
  carId: mongoose.Schema.Types.ObjectId,
  startDate: Date,
  endDate: Date,
  totalPrice: Number
});
module.exports = mongoose.model("Booking", BookingSchema);
