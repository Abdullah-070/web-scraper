import express from 'express';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';
import { getAllUsers, deleteUserController } from '../controllers/userController.js';

const router = express.Router();

router.get("/users", authMiddleware, roleMiddleware('admin'), getAllUsers);
router.delete("/users/:id", authMiddleware, roleMiddleware('admin'), deleteUserController);

export default router;