import { hashPassword, comparePassword } from "../utils/hashPassword.js";
import { generateToken } from "../utils/generateToken.js";
import userModel from "../../../database/models/User.js";
import { sendEmail } from "../utils/sendEmail.js";
import { generateOTP } from "../utils/generateOTP.js";
import { otpEmailTemplate } from "../templates/otpEmailTemplate.js";
import { successResponse, errorResponse } from "../utils/apiResponse.js";

export const registerController = async (req, res) => {
  const { name, email, password } = req.body;

  if (!name || !email || !password) {
    return errorResponse(res, 400, "Please provide all required fields");
  }

  const existingUser = await userModel.findOne({ email });
  if (existingUser) {
    return errorResponse(res, 400, "User already exists with this email");
  }

  const hashedPassword = await hashPassword(password);

  const newUser = await userModel.create({
    name,
    email,
    password: hashedPassword,
    role: "user", // Default role is 'user' if not provided
  });

  return successResponse(res, 201, "User registered successfully", {
    id: newUser._id,
    name: newUser.name,
    email: newUser.email,
    role: newUser.role,
  });
};

export const loginController = async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return errorResponse(res, 400, "Please provide both email and password");
  }

  const user = await userModel.findOne({ email });

  if (!user) {
    return errorResponse(res, 400, "Invalid credentials");
  }

  const isPasswordValid = await comparePassword(password, user.password);

  if (!isPasswordValid) {
    return errorResponse(res, 400, "Invalid credentials");
  }

  const token = generateToken(user._id, user.role);

  res.cookie("token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
    maxAge: 24 * 60 * 60 * 1000,
  });

  return successResponse(res, 200, "Login successful", {
    id: user._id,
    name: user.name,
    email: user.email,
    role: user.role,
  });
};

export const logoutController = (req, res) => {
  res.clearCookie("token", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
  });
  return successResponse(res, 200, "Logout successful");
};

export const getMe = async (req, res) => {
  const user = await userModel.findById(req.user.userId).select("-password");

  if (!user) {
    return errorResponse(res, 404, "User not found");
  }

  return successResponse(res, 200, "User fetched successfully", user);
};

export const forgotPasswordController = async (req, res) => {
  const { email } = req.body;

  const user = await userModel.findOne({ email });

  if (!user) {
    return errorResponse(res, 404, "User not found");
  }

  const otp = generateOTP();

  user.resetOTP = otp;
  user.resetOTPExpiry = Date.now() + 5 * 60 * 1000; // OTP valid for 5 minutes
  user.resetOTPAttempts = 0; // Reset attempts on new OTP generation

  await user.save();

  const htmlContent = otpEmailTemplate(otp);

  await sendEmail(user.email, "Your SDIP Password Reset OTP", htmlContent);

  return successResponse(res, 200, "OTP sent to email");
};

export const verifyOtpController = async (req, res) => {
  const { email, otp } = req.body;

  const user = await userModel.findOne({ email });

  if (!user) {
    return errorResponse(res, 404, "User not found");
  }

  if (user.resetOTP === null) {
    return errorResponse(res, 400, "No OTP found, please request a new one.");
  }

  if (user.resetOTPExpiry < Date.now()) {
    user.resetOTP = null;
    user.resetOTPExpiry = null;
    user.resetOTPAttempts = 0;
    await user.save();
    return errorResponse(res, 400, "OTP has expired");
  }

  if (user.resetOTP !== otp) {
    user.resetOTPAttempts += 1;
    if (user.resetOTPAttempts >= 3) {
      user.resetOTP = null;
      user.resetOTPExpiry = null;
      user.resetOTPAttempts = 0;
      await user.save();
      return errorResponse(
        res,
        400,
        "Maximum OTP attempts exceeded. Please request a new OTP.",
      );
    }

    await user.save();
    return errorResponse(res, 400, "Invalid OTP");
  }

  user.otpVerified = true;
  await user.save();

  return successResponse(res, 200, "OTP verified successfully");
};

export const resetPasswordController = async (req, res) => {
  const { email, newPassword } = req.body;

  const user = await userModel.findOne({ email });

  if (!user) {
    return errorResponse(res, 404, "User not found");
  }

  if (!user.otpVerified) {
    return errorResponse(
      res,
      400,
      "OTP not verified. Please verify OTP before resetting password.",
    );
  }

  const hashedPassword = await hashPassword(newPassword);
  user.password = hashedPassword;
  user.resetOTP = null;
  user.resetOTPExpiry = null;
  user.resetOTPAttempts = 0;
  user.otpVerified = false;

  await user.save();

  return successResponse(res, 200, "Password reset successful");
};
