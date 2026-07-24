import resultModel from '../../../database/models/Result.js';
import jobModel from '../../../database/models/Job.js';
export const getResultsByJobId = async (req, res) => {
    const jobId = req.params.jobId;

    const job = await jobModel.findById(jobId);

    if(!job) {
        return res.status(404).json({ message: 'Job not found' });
    }

    if(job.userId.toString() !== req.user.userId) {
        return res.status(403).json({ message: 'You are not authorized to view this job results' });
    }

    const results = await resultModel.find({ jobId: jobId });

    if(!results || results.length === 0) {
        return res.status(404).json({ message: 'No results found for this job' });
    }

    res.status(200).json({
        message: 'Job results fetched successfully',
        results: results
    })
}