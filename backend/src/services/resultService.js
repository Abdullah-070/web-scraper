import resultModel from '../../../database/models/Result.js';
import jobModel from '../../../database/models/Job.js';

export const getResultsByJobIdService = async (jobId, userId) => {
    const job = await jobModel.findById(jobId);

    if(!job) {
        return { error: true, statusCode: 404, message: 'Job not found' };
    }

    if(job.userId.toString() !== userId) {
        return { error: true, statusCode: 403, message: 'You are not authorized to view this job results' };
    }

    const results = await resultModel.find({ jobId: jobId });

    if(!results || results.length === 0) {
        return { error: true, statusCode: 404, message: 'No results found for this job' };
    }

    return { error: false, statusCode: 200, message: 'Job results fetched successfully', data: results };
};
