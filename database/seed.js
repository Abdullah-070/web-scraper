import connectDB from "./connection.js";
import User from "./models/User.js";
import { hashPassword } from "../backend/src/utils/hashPassword.js";
import dotenv from "dotenv";

dotenv.config({
    path: "../backend/.env"
})
const seedAdmin = async () => {
  try {
    await connectDB();

    const existingAdmin = await User.findOne({ role: "admin" });
    if (existingAdmin) {
      console.log("Admin already exists. Skipping seed.");
      process.exit(0);
    }

    const hashedPassword = await hashPassword("admin123");

    const admin = await User.create({
      name: "Admin",
      email: "admin@sdip.com",
      password: hashedPassword,
      role: "admin",
    });

    console.log("Admin created successfully:", admin.email);
    process.exit(0);
  } catch (error) {
    console.error("Seeding failed:", error.message);
    process.exit(1);
  }
};

seedAdmin();