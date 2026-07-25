import { errorResponse } from "../utils/apiResponse.js";
import * as exportService from "../services/exportService.js";

export const exportResultController = async (req, res) => {
  try {
    const result = await exportService.exportResultService(
        req.params.jobId, 
        req.query.format, 
        req.user.userId
    );

    if (result.error) {
      return errorResponse(res, result.statusCode, result.message);
    }

    if (result.format === "csv") {
      res
        .status(200)
        .header("Content-Type", result.contentType)
        .header("Content-Disposition", `attachment; filename=${result.filename}`)
        .send(result.data);
    } else {
      res.setHeader("Content-Type", result.contentType);
      res.setHeader("Content-Disposition", `attachment; filename=${result.filename}`);
      res.send(result.data);
    }
  } catch (error) {
    return errorResponse(res, 500, "Internal Server Error");
  }
};
