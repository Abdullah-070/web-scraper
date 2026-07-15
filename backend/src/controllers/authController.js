import {hashPassword, comparePassword} from '../utils/hashPassword.js';
import {generateToken} from '../utils/generateToken.js';
import userModel from '../../../database/models/User.js';

export const registerController = async (req, res) => {
    const { name, email, password } = req.body;

    if(!name || !email || !password) {
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
        user: {id: newUser._id, name: newUser.name, email: newUser.email, role: newUser.role},
    });

}

export const loginController = async (req, res) => {
    const { email, password } = req.body;

    if(!email || !password) {
        return res.status(400).json({ message: 'Please provide all required fields' });
    }

    const user = await userModel.findOne({ email });

    if(!user) {
        return res.status(400).json({ message: 'Invalid credentials email' });
    }

    const isPasswordValid = await comparePassword(password, user.password);

    if(!isPasswordValid) {
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
        token,
        user: {id: user._id, name: user.name, email: user.email, role: user.role},
    })
}

export const getMe = async (req, res) => {
    console.log(req.user);
    const user = await userModel.findById(req.user.userId).select('-password');

    if(!user) {
        return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({
        message: 'User found',
        user
    });
}