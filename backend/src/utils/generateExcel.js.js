import ExcelJS from 'exceljs';

export const generateExcel = async (results) => {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Results');
    if (results.length > 0) {
        const sampleData = results[0].data;
        const columns = Object.keys(sampleData).map((key) => ({
            header: key.charAt(0).toUpperCase() + key.slice(1),
            key: key,
            width: 20,
        }))
        worksheet.columns = columns;

        results.forEach((result) => {
            worksheet.addRow(result.data);
        })
    }

    const buffer = await workbook.xlsx.writeBuffer();

    return buffer;
}