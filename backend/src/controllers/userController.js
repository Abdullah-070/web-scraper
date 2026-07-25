import { successResponse, errorResponse } from '../utils/apiResponse.js';
import * as userService from '../services/userService.js';

export const getAllUsers = async (req, res) => {
    try {
        const result = await userService.getAllUsersService();
        if (result.error) {
            return errorResponse(res, result.statusCode, result.message);
        }
        return successResponse(res, result.statusCode, result.message, result.data);
    } catch (error) {
        return errorResponse(res, 500, "Internal Server Error");
    }
}

export const deleteUserController = async (req, res) => {
    try {
        const result = await userService.deleteUserService(req.params.id);
        if (result.error) {
            return errorResponse(res, result.statusCode, result.message);
        }
        return successResponse(res, result.statusCode, result.message);
    } catch (error) {
        return errorResponse(res, 500, "Internal Server Error");
    }
}