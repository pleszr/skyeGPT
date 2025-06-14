import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from 'child_process';
import { config as loadEnv } from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// CONFIG
const devMode = process.env.DEV_MODE === 'true' || process.argv.includes('--dev');
const setEnvOnly = process.argv.includes('--setenv-only');

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

const DEV_VERSION = '9.9.9.9';

function getVersion() {
    if (devMode) {
        console.log('Dev mode enabled - using dev version');
        return DEV_VERSION;
    }

    try {
        const result = execSync('git tag --sort=-version:refname', { encoding: 'utf8', stdio: 'pipe' });
        const tags = result.trim().split('\n').filter(tag => tag.trim());
        return tags.length > 0 ? tags[0].trim() : DEV_VERSION;
    } catch {
        console.log('Could not get git tags, using dev mode - please check YOUR GIT CONFIG');
        return DEV_VERSION;
    }
}

function updatePackageJson(version, projectRoot) {
    try {
        const packagePath = path.join(projectRoot, 'package.json');
        if (!fs.existsSync(packagePath)) return false;

        const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        packageJson.version = version;
        fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2));
        return true;
    } catch (error) {
        console.error('Error updating package.json:', error.message);
        return false;
    }
}

try {
    const projectRoot = findProjectRoot(__dirname);
    const configPath = path.join(projectRoot, "public/skyeconfig.json");

    if (devMode) {
        const envPath = path.join(projectRoot, '.env');
        if (fs.existsSync(envPath)) {
            loadEnv({ path: envPath });
            console.log('Dev mode: Loaded .env file');
        } else {
            console.log('Dev mode: No .env file found, using environment variables');
        }
    }

    const backendHost = process.env.BACKEND_HOST || "http://localhost:8000";

    let config = {};
    if (fs.existsSync(configPath)) {
        try {
            config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        } catch {
            console.log('Invalid JSON in skyeconfig.json, creating fresh config');
        }
    }

    if (setEnvOnly) {
        if (process.env.BACKEND_HOST) {
            config.backendHost = process.env.BACKEND_HOST;
            fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

            console.log('Updated backend host from environment variable');
            console.log(`backendHost: ${process.env.BACKEND_HOST}`);
            console.log(`UPDATED ${configPath}`);
        } else {
            console.log('No BACKEND_HOST environment variable found, no changes made');
        }
    } else {
        const version = getVersion();

        config.backendHost = backendHost;
        config.version = version;
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

        const packageUpdated = updatePackageJson(version, projectRoot);

        const modeLabel = devMode ? 'Dev mode' : 'Config UPDATED';
        console.log(`${modeLabel}:`);
        console.log(`backendHost: ${backendHost}`);
        console.log(`version: ${version}`);
        if (packageUpdated) {
            console.log(`UPDATED package.json`);
        }
        console.log(`UPDATED ${configPath}`);
    }

} catch (error) {
    console.error('ERROR during setup:', error.message);
}