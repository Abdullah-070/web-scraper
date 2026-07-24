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

export const deleteUserController = async (req, res) => {
    const userId = req.params.id;

    const user = await userModel.findById(userId);

    if (!user) {
        return res.status(404).json({ message: 'User not found' });
    }

    if(user.role === 'admin') {
        return res.status(403).json({ message: 'Cannot delete admin user' });
    }

    await userModel.findByIdAndDelete(userId);

    res.status(200).json({ message: 'User deleted successfully' });

}