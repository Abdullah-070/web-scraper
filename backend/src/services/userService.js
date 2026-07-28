import userModel from '../../../database/models/User.js';
import logger from '../config/logger.js';

export const getAllUsersService = async () => {
    const users = await userModel.find({}, '-password'); // Exclude password field
    return { error: false, statusCode: 200, message: 'Users fetched successfully', data: users };
};

export const deleteUserService = async (userId) => {
    const user = await userModel.findById(userId);

    if (!user) {
        return { error: true, statusCode: 404, message: 'User not found' };
    }

    if(user.role === 'admin') {
        logger.warn("Attempt to delete an admin user blocked", { userId });
        return { error: true, statusCode: 403, message: 'Cannot delete admin user' };
    }

    await userModel.findByIdAndDelete(userId);

    logger.info("User deleted", { userId });
    return { error: false, statusCode: 200, message: 'User deleted successfully' };
};
