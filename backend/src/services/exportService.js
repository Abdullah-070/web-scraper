import jobModel from "../../../database/models/Job.js";
import resultModel from "../../../database/models/Result.js";
import { generateExcel } from "../utils/generateExcel.js.js";
import { generateCSV } from "../utils/generateCSV.js";

export const exportResultService = async (jobId, format, userId) => {
  const job = await jobModel.findById(jobId);

  if (!job) {
    return { error: true, statusCode: 404, message: "Job not found" };
  }

  if (job.userId.toString() !== userId) {
    return { error: true, statusCode: 403, message: "You are not authorized to export this job result" };
  }

  const results = await resultModel.find({ jobId: jobId });

  if (format === "csv") {
    const csv = generateCSV(results);
    return { 
        error: false, 
        format: "csv", 
        contentType: "text/csv", 
        filename: "results.csv", 
        data: csv 
    };
  } else if (format === "excel") {
    const buffer = await generateExcel(results);
    return { 
        error: false, 
        format: "excel", 
        contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        filename: "results.xlsx", 
        data: buffer 
    };
  } else if (format === "json") {
    const exportData = results.map((r) => r.data);
    return { 
        error: false, 
        format: "json", 
        contentType: "application/json", 
        filename: "results.json", 
        data: JSON.stringify(exportData, null, 2) 
    };
  } else {
    return { error: true, statusCode: 400, message: "Invalid format. Only csv is supported" };
  }
};
