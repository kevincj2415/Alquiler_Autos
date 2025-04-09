const mongoose = require('mongoose');

const URI = 'mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/';

const conectarDB = async () => {
  try {
    await mongoose.connect(URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('✅ Conectado a MongoDB');
  } catch (error) {
    console.error('❌ Error al conectar a MongoDB:', error);
    process.exit(1);
  }
};

module.exports = conectarDB;
