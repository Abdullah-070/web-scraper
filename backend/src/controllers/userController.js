import { successResponse, errorResponse } from '../utils/apiResponse.js';
import * as userService from '../services/userService.js';
import logger from '../config/logger.js';

export const getAllUsers = async (req, res) => {
    try {
        const result = await userService.getAllUsersService();
        if (result.error) {
            return errorResponse(res, result.statusCode, result.message);
        }
        return successResponse(res, result.statusCode, result.message, result.data);
    } catch (error) {
        logger.error("Error in getAllUsers", { error: error.message });
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
        logger.error("Error in deleteUserController", { error: error.message });
        return errorResponse(res, 500, "Internal Server Error");
    }
}