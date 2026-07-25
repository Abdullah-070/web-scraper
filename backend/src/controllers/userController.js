import userModel from '../../../database/models/User.js';
import { successResponse, errorResponse } from '../utils/apiResponse.js';

export const getAllUsers = async (req, res) => {

        const users = await userModel.find({}, '-password'); // Exclude password field
        return successResponse(res, 200, 'Users fetched successfully', users);
    
}

export const deleteUserController = async (req, res) => {
    const userId = req.params.id;

    const user = await userModel.findById(userId);

    if (!user) {
        return errorResponse(res, 404, 'User not found');
    }

    if(user.role === 'admin') {
        return errorResponse(res, 403, 'Cannot delete admin user');
    }

    await userModel.findByIdAndDelete(userId);

    return successResponse(res, 200, 'User deleted successfully');

}