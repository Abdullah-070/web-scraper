import { hashPassword, comparePassword } from '../utils/hashPassword.js';
import { generateToken } from '../utils/generateToken.js';
import userModel from '../../../database/models/User.js';
import { sendEmail } from '../utils/sendEmail.js';
import { generateOTP } from '../utils/generateOTP.js';
import { otpEmailTemplate } from '../templates/otpEmailTemplate.js';

export const registerController = async (req, res) => {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
        return res.status(400).json({ message: 'Please provide all required fields' });
    }

    const existingUser = await userModel.findOne({ email });
    if (existingUser) {
        return res.status(400).json({ message: 'User already exists' });
    }

    const hashedPassword = await hashPassword(password);

    const newUser = await userModel.create({
        name,
        email,
        password: hashedPassword,
        role: 'user' // Default role is 'user' if not provided
    })

    res.status(201).json({
        message: 'User registered successfully',
        user: { id: newUser._id, name: newUser.name, email: newUser.email, role: newUser.role },
    });

}

export const loginController = async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ message: 'Please provide all required fields' });
    }

    const user = await userModel.findOne({ email });

    if (!user) {
        return res.status(400).json({ message: 'Invalid credentials email' });
    }

    const isPasswordValid = await comparePassword(password, user.password);

    if (!isPasswordValid) {
        return res.status(400).json({ message: 'Invalid credentials' });
    }

    const token = generateToken(user._id, user.role);

    res.cookie('token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',
        maxAge: 24 * 60 * 60 * 1000,
    });

    res.status(200).json({
        message: 'Login successful',
        user: { id: user._id, name: user.name, email: user.email, role: user.role },
    })
}

export const logoutController = (req, res) => {
    res.clearCookie('token', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',
    });
    res.status(200).json({ message: 'Logout successful' });
}

export const getMe = async (req, res) => {
    console.log(req.user);
    const user = await userModel.findById(req.user.userId).select('-password');

    if (!user) {
        return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({
        message: 'User found',
        user
    });
}

export const forgotPasswordController = async (req, res) => {
    try {
        const { email } = req.body;

        const user = await userModel.findOne({ email })

        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }

        const otp = generateOTP();

        user.resetOTP = otp;
        user.resetOTPExpiry = Date.now() + 5 * 60 * 1000; // OTP valid for 5 minutes
        user.resetOTPAttempts = 0; // Reset attempts on new OTP generation

        await user.save();

        const htmlContent = otpEmailTemplate(otp);

        await sendEmail(user.email, 'Your SDIP Password Reset OTP', htmlContent);

        res.status(200).json({ message: 'OTP sent to email' });
    } catch (error) {
        res.status(500).json({ message: 'Error occurred while processing forgot password request' });
    }
}

export const verifyOtpController = async (req, res) => {
    const { email, otp } = req.body;

    const user = await userModel.findOne({ email });

    if (!user) {
        return res.status(404).json({ message: 'User not found' });
    }

    if(user.resetOTP === null){
        return res.status(400).json({message: 'No OTP found, please request a new one.'})
    }

    if (user.resetOTPExpiry < Date.now()) {
        user.resetOTP = null;
        user.resetOTPExpiry = null;
        user.resetOTPAttempts = 0;
        await user.save();
        return res.status(400).json({ message: 'OTP has expired' });
    }

    if (user.resetOTP !== otp) {
        user.resetOTPAttempts += 1;
        if(user.resetOTPAttempts >= 3){
            user.resetOTP = null;
            user.resetOTPExpiry = null;
            user.resetOTPAttempts = 0;
            await user.save();
            return res.status(400).json({ message: 'Maximum OTP attempts exceeded. Please request a new OTP.' });   
        }

        await user.save();
        return res.status(400).json({ message: 'Invalid OTP' });
        
    }

    user.otpVerified = true;
    await user.save();

    res.status(200).json({ message: 'OTP verified successfully' });

} 

export const resetPasswordController = async (req, res) => {
    const { email, newPassword } = req.body;

    const user = await userModel.findOne({ email });

    if(!user){
        return res.status(404).json({ message: 'User not found' });
    }

    if(!user.otpVerified){
        return res.status(400).json({ message: 'OTP not verified. Please verify OTP before resetting password.' });
    }

    const hashedPassword = await hashPassword(newPassword);
    user.password = hashedPassword;
    user.resetOTP = null;
    user.resetOTPExpiry = null;
    user.resetOTPAttempts = 0;
    user.otpVerified = false;

    await user.save();

    res.status(200).json({ message: 'Password reset successful' });
}