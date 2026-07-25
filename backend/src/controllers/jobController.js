import jobModel from "../../../database/models/Job.js";
import redisClient from "../config/redis.js";
import { successResponse, errorResponse } from "../utils/apiResponse.js";

export const createJobController = async (req, res) => {
  const { scraperType, inputParams } = req.body;

  const newJob = await jobModel.create({
    userId: req.user.userId,
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
    }),
  );

  return successResponse(res, 201, "Job created successfully", newJob);
};

export const getUserJobs = async (req, res) => {
  const userId = req.user.userId;

  const jobs = await jobModel.find({
    userId: userId,
  });

  if (!jobs || jobs.length === 0) {
    return errorResponse(res, 404, "No jobs found for this user");
  }

  return successResponse(res, 200, "User jobs fetched successfully", jobs);
};

export const getJobById = async (req, res) => {
  const jobId = req.params.id;

  const job = await jobModel.findById(jobId);

  if (job.userId.toString() !== req.user.userId) {
    return errorResponse(res, 403, "You are not authorized to view this job");
  }

  if (!job) {
    return errorResponse(res, 404, "Job not found");
  }

  return successResponse(res, 200, "Job fetched successfully", job);
};
