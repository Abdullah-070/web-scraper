import { Parser } from 'json2csv';

export const generateCSV = (results) => {
    const parser = new Parser();
    const resultsArray = results.map(result => result.data);
    const csv = parser.parse(resultsArray);
    return csv;
}