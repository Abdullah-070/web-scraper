import express from 'express';
import { registerController, loginController, getMe, logoutController, forgotPasswordController, verifyOtpController, resetPasswordController } from '../controllers/authController.js';
import { authMiddleware } from '../middlewares/authMiddleware.js';
import { roleMiddleware } from '../middlewares/roleMiddleware.js';
import validate from '../middlewares/validate.js'
import { signupSchema, signinSchema, forgotPasswordSchema, verifyOTPSchema, resetPasswordSchema } from '../validators/authValidator.js';

const router = express.Router();

router.post('/register', validate(signupSchema),registerController);
router.post('/login', validate(signinSchema),loginController);
router.post('/logout', authMiddleware, logoutController);
router.post('/forgot-password', validate(forgotPasswordSchema),forgotPasswordController);
router.post('/verify-otp', validate(verifyOTPSchema), verifyOtpController);
router.post('/reset-password', validate(resetPasswordSchema), resetPasswordController);
router.get('/me', authMiddleware, roleMiddleware('user', 'admin'), getMe);

export default router;