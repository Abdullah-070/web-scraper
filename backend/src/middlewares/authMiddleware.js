import jwt from 'jsonwebtoken';
import { successResponse, errorResponse } from '../utils/apiResponse.js';

export const authMiddleware = (req, res, next) => {

    const token = req.cookies.token;
    if (!token) {
        return errorResponse(res, 401, 'Unauthorized: No token provided');
    }

    try{
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    }catch(error){
        return errorResponse(res, 401, 'Unauthorized: Invalid token');
    }
}