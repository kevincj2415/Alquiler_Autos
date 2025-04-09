const express = require('express');
const cors = require('cors');
const conectarDB = require('./config/db');
const alquilerRoutes = require('./routes/booking.routes');

const app = express();
conectarDB();

app.use(cors());
app.use(express.json());

app.use('/api/alquiler', alquilerRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en el puerto ${PORT}`);
});
