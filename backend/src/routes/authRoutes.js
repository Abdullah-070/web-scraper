import express from 'express';
import { registerController, loginController, getMe, logoutController, forgotPasswordController, verifyOtpController, resetPasswordController } from '../controllers/authController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';
import { getAllUsers } from '../controllers/userController.js';

const router = express.Router();

router.post('/register', registerController);
router.post('/login', loginController);
router.post('/logout', authMiddleware, logoutController);
router.post('/forgot-password', forgotPasswordController);
router.post('/verify-otp', verifyOtpController);
router.post('/reset-password', resetPasswordController);
router.get('/me', authMiddleware, roleMiddleware('user', 'admin'), getMe);

export default router;