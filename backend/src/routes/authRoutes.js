import express from 'express';
import { registerController, loginController, getMe } from '../controllers/authController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';
import { getAllUsers } from '../controllers/userController.js';

const router = express.Router();

router.post('/register', registerController);
router.post('/login', loginController);
router.get('/me', authMiddleware, roleMiddleware('user', 'admin'), getMe);
router.get("/users", authMiddleware, roleMiddleware('admin'), getAllUsers);

export default router;