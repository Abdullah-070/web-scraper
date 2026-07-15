import userModel from '../../../database/models/User.js';
export const getAllUsers = async (req, res) => {
    try {
        const users = await userModel.find({}, '-password'); // Exclude password field
        res.status(200).json({ users });
    } catch (error) {
        console.error('Error fetching users:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
}