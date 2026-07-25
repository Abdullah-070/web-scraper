import { successResponse, errorResponse } from '../utils/apiResponse.js';
import * as resultService from '../services/resultService.js';

export const getResultsByJobId = async (req, res) => {
    try {
        const result = await resultService.getResultsByJobIdService(req.params.jobId, req.user.userId);
        if (result.error) {
            return errorResponse(res, result.statusCode, result.message);
        }
        return successResponse(res, result.statusCode, result.message, result.data);
    } catch (error) {
        return errorResponse(res, 500, "Internal Server Error");
    }
}