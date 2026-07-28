import jobModel from "../../../database/models/Job.js";
import redisClient from "../config/redis.js";
import logger from "../config/logger.js";

export const createJobService = async (data, userId) => {
  const { scraperType, inputParams } = data;

  const newJob = await jobModel.create({
    userId: userId,
    scraperType,
    inputParams,
    status: "pending",
  });

  redisClient.lpush(
    "jobQueue",
    JSON.stringify({
      jobId: newJob._id,
      scraperType: newJob.scraperType,
      inputParams: newJob.inputParams,
    })
  );

  logger.info("Job created and queued", { jobId: newJob._id, scraperType: newJob.scraperType, userId });
  return { error: false, statusCode: 201, message: "Job created successfully", data: newJob };
};

export const getUserJobsService = async (userId) => {
  const jobs = await jobModel.find({
    userId: userId,
  });

  if (!jobs || jobs.length === 0) {
    return { error: true, statusCode: 404, message: "No jobs found for this user" };
  }

  return { error: false, statusCode: 200, message: "User jobs fetched successfully", data: jobs };
};

export const getJobByIdService = async (jobId, userId) => {
  const job = await jobModel.findById(jobId);

  if (!job) {
    return { error: true, statusCode: 404, message: "Job not found" };
  }

  if (job.userId.toString() !== userId) {
    return { error: true, statusCode: 403, message: "You are not authorized to view this job" };
  }

  return { error: false, statusCode: 200, message: "Job fetched successfully", data: job };
};
