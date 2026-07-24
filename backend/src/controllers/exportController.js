import jobModel from '../../../database/models/Job.js';
import resultModel from '../../../database/models/Result.js';
import { generateExcel } from '../utils/generateExcel.js.js';
import { generateCSV } from '../utils/generateCSV.js';
export const exportResultController = async (req, res) => {

    const jobId = req.params.jobId;
    const format = req.query.format;

    const job = await jobModel.findById(jobId);

    if (!job) {
        return res.status(404).json({ message: 'Job not found' });
    }

    if (job.userId.toString() !== req.user.userId) {
        return res.status(403).json({ message: 'You are not authorized to export this job result' });
    }


    const results = await resultModel.find({ jobId: jobId });

    if (format === 'csv') {
        const csv = generateCSV(results);
        res.status(200)
            .header('Content-Type', 'text/csv')
            .header('Content-Disposition', "attachment; filename=results.csv")
            .send(csv);
    }
    else if (format === 'excel') {

        const buffer = await generateExcel(results);

        res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        res.setHeader("Content-Disposition", "attachment; filename=results.xlsx");
        res.send(buffer);
    }
    else if (format === "json") {
        const exportData = results.map((r) => r.data);

        res.setHeader("Content-Type", "application/json");
        res.setHeader("Content-Disposition", "attachment; filename=results.json");
        res.send(JSON.stringify(exportData, null, 2));
    }
    else {
        return res.status(400).json({ message: 'Invalid format. Only csv is supported' });
    }
}