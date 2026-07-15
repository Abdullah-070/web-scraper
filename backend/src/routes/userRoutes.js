import express from 'express';
import { registerController, loginController, getMe } from '../controllers/authController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';
import { getAllUsers } from '../controllers/userController.js';

const router = express.Router();

router.get("/users", authMiddleware, roleMiddleware('admin'), getAllUsers);

export default router;