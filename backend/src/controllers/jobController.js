import jobModel from '../../../database/models/Job.js';
import redisClient from '../config/redis.js';
export const createJobController = async (req, res) => {
    const {scraperType, inputParams} = req.body;

    const newJob = await jobModel.create({
        userId: req.user.userId,
        scraperType,
        inputParams,
        status: 'pending'
    })

    redisClient.lpush('jobQueue', JSON.stringify({
        jobId: newJob._id,
        scraperType: newJob.scraperType,
        inputParams: newJob.inputParams
    }))

    res.status(201).json({
        message: 'Job created successfully',
        job: newJob
    })

}

export const getUserJobs = async (req, res) => {
    const userId = req.user.userId;

    const jobs = await jobModel.find({
        userId: userId
    })

    if(!jobs || jobs.length === 0) {
        return res.status(404).json({ message: 'No jobs found for this user' });
    }

    res.status(200).json({
        message: 'User jobs fetched successfully',
        jobs: jobs
    })
}

export const getJobById = async (req, res) => {
    const jobId = req.params.id;

    const job = await jobModel.findById(jobId);

    if(job.userId.toString() !== req.user.userId) {
        return res.status(403).json({ message: 'You are not authorized to view this job' });
    }

    if(!job) {
        return res.status(404).json({ message: 'Job not found' });
    }

    res.status(200).json({
        message: 'Job fetched successfully',
        job: job
    })
}

