import { z } from "zod";

export const createJobSchema = z.object({
  scraperType: z.string().min(1, "Scraper type is required"),
  inputParams: z.record(z.any()).refine((obj) => Object.keys(obj).length > 0, {
    message: "inputParams cannot be empty",
  }),
});
