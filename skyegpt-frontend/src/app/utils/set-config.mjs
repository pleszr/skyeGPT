import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const backendHost = process.env.BACKEND_HOST_URL || "http://localhost:8000";
const config = { backendHost };

const configPath = path.join(__dirname, "../../../public/skyeconfig.json");
fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
console.log(`Wrote backendHost=${backendHost} to ${configPath}`);

