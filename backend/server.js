import 'dotenv/config';
import './src/config/redis.js';
import app from './src/app.js';
import connectDB from '../database/connection.js';
import logger from './src/config/logger.js';


const PORT = process.env.PORT || 3000;
    
connectDB();

app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`);
})