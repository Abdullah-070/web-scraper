import mongoose from "mongoose";

const resultSchema = new mongoose.Schema(
	{
		jobId: {
			type: mongoose.Schema.Types.ObjectId,
			ref: "Job",
			required: true,
		},
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
		data: {
			type: mongoose.Schema.Types.Mixed,
			required: true,
		},
	},
	{ timestamps: true }
);

const resultModel = mongoose.model("Result", resultSchema);

export default resultModel;
