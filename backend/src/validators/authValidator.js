import {z} from 'zod';

export const signupSchema = z.object({
    name: z.string().min(3, "Name must be atleast 3 characters"),
    email: z.email("Invalid Email Address"),
    password: z.string().min(6, "Password must be atleast 6 characters")
})


export const signinSchema = z.object({
    email: z.email("Invalid Email Address"),
    password: z.string().min(6, "Password must be atleast 6 characters")
})

export const forgotPasswordSchema = z.object({
    email: z.email("Invalid Email Address")
})

export const verifyOTPSchema = z.object({
    email: z.email("Invalid Email Address"),
    otp: z.string().length(6, "OTP must be 6 digits")
})

export const resetPasswordSchema = z.object({
    email: z.email("Invalid Email Address"),
    password: z.string().min(6, "Password must be atleast 6 characters")
})