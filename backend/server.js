import 'dotenv/config';
import './src/config/redis.js';
import app from './src/app.js';
import connectDB from '../database/connection.js';


const PORT = process.env.PORT || 3000;
    
connectDB();

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
})