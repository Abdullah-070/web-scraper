import Redis from "ioredis";
import logger from "./logger.js";

const redisClient = new Redis(process.env.REDIS_URL);

redisClient.on("connect", () => {
    logger.info("Connected to Redis");
});

redisClient.on("error", (err) => {
    logger.error("Redis connection error", { error: err.message });
});

export default redisClient;