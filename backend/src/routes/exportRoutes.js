import express from 'express';
import { exportResultController } from '../controllers/exportController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';

const router = express.Router();

router.get('/:jobId', authMiddleware, roleMiddleware('user'), exportResultController);

export default router;