const express = require('express');
const router = express.Router();
const Auto = require('../models/Car.js');

// Obtener todos los autos
router.get('/autos', async (req, res) => {
  try {
    const autos = await Auto.find();
    res.json(autos);
  } catch (err) {
    res.status(500).json({ mensaje: 'Error al obtener los autos' });
  }
});

// Crear un nuevo auto
router.post('/autos', async (req, res) => {
  try {
    const nuevoAuto = new Auto(req.body);
    await nuevoAuto.save();
    res.status(201).json(nuevoAuto);
  } catch (err) {
    res.status(400).json({ mensaje: 'Error al guardar el auto' });
  }
});

module.exports = router;
