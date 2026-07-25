import { successResponse, errorResponse } from "../utils/apiResponse.js";

export const roleMiddleware = (...requiredRoles) => {

    return (req, res, next) => {
        const userRole = req.user.role;
        if (!requiredRoles.includes(userRole)) {
            return errorResponse(res, 403, 'Forbidden: Insufficient role');
        }
        next();
    }
}