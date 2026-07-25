import resultModel from '../../../database/models/Result.js';
import jobModel from '../../../database/models/Job.js';
import { successResponse, errorResponse } from '../utils/apiResponse.js';
export const getResultsByJobId = async (req, res) => {
    const jobId = req.params.jobId;

    const job = await jobModel.findById(jobId);

    if(!job) {
        return errorResponse(res, 404, 'Job not found');
    }

    if(job.userId.toString() !== req.user.userId) {
        return errorResponse(res, 403, 'You are not authorized to view this job results');
    }

    const results = await resultModel.find({ jobId: jobId });

    if(!results || results.length === 0) {
        return errorResponse(res, 404, 'No results found for this job');
    }

    return successResponse(res, 200, 'Job results fetched successfully', results);
}