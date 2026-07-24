import express from 'express';
import { getResultsByJobId } from '../controllers/resultController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';

const router = express.Router();

router.get("/:jobId", authMiddleware, roleMiddleware('user'), getResultsByJobId);

export default router;