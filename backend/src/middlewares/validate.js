import { errorResponse } from "../utils/apiResponse.js";

const validate = (schema) => {
  return async (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      const firstError = result.error.issues[0].message;
      return errorResponse(res, 400, firstError);
    }
    
    req.body = result.data;
    next();
  };
};

export default validate;
