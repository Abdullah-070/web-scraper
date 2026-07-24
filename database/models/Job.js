import mongoose from "mongoose";

const jobSchema = new mongoose.Schema(
	{
		userId: {
			type: mongoose.Schema.Types.ObjectId,
			ref: "User",
			required: true,
		},
		scraperType: {
			type: String,
			required: true,
			trim: true,
		},
		inputParams: {
			type: mongoose.Schema.Types.Mixed,
			required: true,
		},
		status: {
			type: String,
			enum: ["pending", "running", "completed", "failed"],
			default: "pending",
		},
	},
	{ timestamps: true }
);

const jobModel = mongoose.model("Job", jobSchema);

export default jobModel;
