import { successResponse, errorResponse } from "../utils/apiResponse.js";
import * as jobService from "../services/jobService.js";
import logger from "../config/logger.js";

export const createJobController = async (req, res) => {
  try {
    const result = await jobService.createJobService(req.body, req.user.userId);
    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }
    return successResponse(res, result.statusCode, result.message, result.data);
  } catch (error) {
    logger.error("Error in createJobController", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const getUserJobs = async (req, res) => {
  try {
    const result = await jobService.getUserJobsService(req.user.userId);
    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }
    return successResponse(res, result.statusCode, result.message, result.data);
  } catch (error) {
    logger.error("Error in getUserJobs", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};

export const getJobById = async (req, res) => {
  try {
    const result = await jobService.getJobByIdService(req.params.id, req.user.userId);
    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }
    return successResponse(res, result.statusCode, result.message, result.data);
  } catch (error) {
    logger.error("Error in getJobById", { error: error.message });
    return errorResponse(res, 500, "Internal Server Error");
  }
};
