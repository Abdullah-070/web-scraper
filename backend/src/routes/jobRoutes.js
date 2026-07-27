import express from 'express';
import { createJobController, getUserJobs, getJobById } from '../controllers/jobController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';
import { createJobSchema } from '../validators/jobValidator.js';
import validate from '../middlewares/validate.js';

const router = express.Router();

router.post('/', authMiddleware, roleMiddleware('user'), validate(createJobSchema), createJobController);
router.get("/", authMiddleware, roleMiddleware('user'), getUserJobs);
router.get("/:id", authMiddleware, roleMiddleware('user'), getJobById);

export default router;