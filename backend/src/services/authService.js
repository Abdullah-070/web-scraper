import { hashPassword, comparePassword } from "../utils/hashPassword.js";
import { generateToken } from "../utils/generateToken.js";
import userModel from "../../../database/models/User.js";
import { sendEmail } from "../utils/sendEmail.js";
import { generateOTP } from "../utils/generateOTP.js";
import { otpEmailTemplate } from "../templates/otpEmailTemplate.js";

export const registerUser = async (data) => {
  const { name, email, password } = data;
  if (!name || !email || !password) {
    return { error: true, statusCode: 400, message: "Please provide all required fields" };
  }

  const existingUser = await userModel.findOne({ email });
  if (existingUser) {
    return { error: true, statusCode: 400, message: "User already exists with this email" };
  }

  const hashedPassword = await hashPassword(password);

  const newUser = await userModel.create({
    name,
    email,
    password: hashedPassword,
    role: "user", // Default role is 'user' if not provided
  });

  return {
    error: false,
    statusCode: 201,
    message: "User registered successfully",
    data: {
      id: newUser._id,
      name: newUser.name,
      email: newUser.email,
      role: newUser.role,
    },
  };
};

export const loginUser = async (data) => {
  const { email, password } = data;
  if (!email || !password) {
    return { error: true, statusCode: 400, message: "Please provide both email and password" };
  }

  const user = await userModel.findOne({ email });

  if (!user) {
    return { error: true, statusCode: 400, message: "Invalid credentials" };
  }

  const isPasswordValid = await comparePassword(password, user.password);

  if (!isPasswordValid) {
    return { error: true, statusCode: 400, message: "Invalid credentials" };
  }

  const token = generateToken(user._id, user.role);

  return {
    error: false,
    statusCode: 200,
    message: "Login successful",
    data: {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
    },
    token,
  };
};

export const getMeUser = async (userId) => {
  const user = await userModel.findById(userId).select("-password");

  if (!user) {
    return { error: true, statusCode: 404, message: "User not found" };
  }

  return {
    error: false,
    statusCode: 200,
    message: "User fetched successfully",
    data: user,
  };
};

export const forgotPasswordUser = async (data) => {
  const { email } = data;
  const user = await userModel.findOne({ email });

  if (!user) {
    return { error: true, statusCode: 404, message: "User not found" };
  }

  const otp = generateOTP();

  user.resetOTP = otp;
  user.resetOTPExpiry = Date.now() + 5 * 60 * 1000; // OTP valid for 5 minutes
  user.resetOTPAttempts = 0; // Reset attempts on new OTP generation

  await user.save();

  const htmlContent = otpEmailTemplate(otp);

  await sendEmail(user.email, "Your SDIP Password Reset OTP", htmlContent);

  return { error: false, statusCode: 200, message: "OTP sent to email" };
};

export const verifyOtpUser = async (data) => {
  const { email, otp } = data;
  const user = await userModel.findOne({ email });

  if (!user) {
    return { error: true, statusCode: 404, message: "User not found" };
  }

  if (user.resetOTP === null) {
    return { error: true, statusCode: 400, message: "No OTP found, please request a new one." };
  }

  if (user.resetOTPExpiry < Date.now()) {
    user.resetOTP = null;
    user.resetOTPExpiry = null;
    user.resetOTPAttempts = 0;
    await user.save();
    return { error: true, statusCode: 400, message: "OTP has expired" };
  }

  if (user.resetOTP !== otp) {
    user.resetOTPAttempts += 1;
    if (user.resetOTPAttempts >= 3) {
      user.resetOTP = null;
      user.resetOTPExpiry = null;
      user.resetOTPAttempts = 0;
      await user.save();
      return {
        error: true,
        statusCode: 400,
        message: "Maximum OTP attempts exceeded. Please request a new OTP.",
      };
    }

    await user.save();
    return { error: true, statusCode: 400, message: "Invalid OTP" };
  }

  user.otpVerified = true;
  await user.save();

  return { error: false, statusCode: 200, message: "OTP verified successfully" };
};

export const resetPasswordUser = async (data) => {
  const { email, newPassword } = data;
  const user = await userModel.findOne({ email });

  if (!user) {
    return { error: true, statusCode: 404, message: "User not found" };
  }

  if (!user.otpVerified) {
    return {
      error: true,
      statusCode: 400,
      message: "OTP not verified. Please verify OTP before resetting password.",
    };
  }

  const hashedPassword = await hashPassword(newPassword);
  user.password = hashedPassword;
  user.resetOTP = null;
  user.resetOTPExpiry = null;
  user.resetOTPAttempts = 0;
  user.otpVerified = false;

  await user.save();

  return { error: false, statusCode: 200, message: "Password reset successful" };
};
