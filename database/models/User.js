import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true,
            trim: true,
        },
        email: {
            type: String,
            required: true,
            unique: true,
            lowercase: true,
            trim: true,
        },
        password: {
            type: String,
            required: true,
        },
        role: {
            type: String,
            enum: ["admin", "user"],
            default: "user",
        },
        resetOTP: {
            type: String,
            default: null,
        },
        resetOTPExpiry: {
            type: Date,
            default: null,
        },
        resetOTPAttempts: {
            type: Number,
            default: 0,
        },
        otpVerified: {
            type: Boolean,
            default: false,
        }
    },
    { timestamps: true }
);

const userModel = mongoose.model("User", userSchema);
export default userModel;