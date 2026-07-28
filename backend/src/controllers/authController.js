import { successResponse, errorResponse } from "../utils/apiResponse.js";
import * as authService from "../services/authService.js";
import logger from "../config/logger.js";

export const registerController = async (req, res) => {
  try {
    const result = await authService.registerUser(req.body);

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    return successResponse(res, result.statusCode, result.message, result.data);
  } catch (error) {
    logger.error("Error in registerController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const loginController = async (req, res) => {
  try {
    const result = await authService.loginUser(req.body);

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    res.cookie("token", result.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
      maxAge: 24 * 60 * 60 * 1000,
    });

    return successResponse(res, result.statusCode, result.message, result.data);
  } catch (error) {
    logger.error("Error in loginController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const logoutController = (req, res) => {
  try {
    res.clearCookie("token", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
    });
    logger.info("User logged out successfully");
    return successResponse(res, 200, "Logout successful");
  } catch (error) {
    logger.error("Error in logoutController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const getMe = async (req, res) => {
  try {
    const result = await authService.getMeUser(req.user.userId);

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    return successResponse(res, result.statusCode, result.message, result.data);
  } catch (error) {
    logger.error("Error in getMe", { error: error.message, userId: req.user?.userId });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const forgotPasswordController = async (req, res) => {
  try {
    const result = await authService.forgotPasswordUser(req.body);

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    return successResponse(res, result.statusCode, result.message);
  } catch (error) {
    logger.error("Error in forgotPasswordController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const verifyOtpController = async (req, res) => {
  try {
    const result = await authService.verifyOtpUser(req.body);

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    return successResponse(res, result.statusCode, result.message);
  } catch (error) {
    logger.error("Error in verifyOtpController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const resetPasswordController = async (req, res) => {
  try {
    const result = await authService.resetPasswordUser(req.body);

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    return successResponse(res, result.statusCode, result.message);
  } catch (error) {
    logger.error("Error in resetPasswordController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};
