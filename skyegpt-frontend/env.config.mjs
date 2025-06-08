import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


const backendHost = process.env.BACKEND_HOST || "http://localhost:8000";

function findProjectRoot(startDir) {
  let currentDir = startDir;
  while (currentDir !== path.parse(currentDir).root) {
    if (fs.existsSync(path.join(currentDir, 'package.json'))) {
      return currentDir;
    }
    currentDir = path.dirname(currentDir);
  }
  throw new Error('Could not find project root (package.json not found)');
}

const projectRoot = findProjectRoot(__dirname);
const configPath = path.join(projectRoot, "public/skyeconfig.json");

let config = {};
if (fs.existsSync(configPath)) {
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    console.log('Invalid JSON in skyeconfig.json, starting fresh');
  }
}

config.backendHost = backendHost;

fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
console.log(`Wrote backendHost=${backendHost} to ${configPath}`);