import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// CONFIG
const backendHost = process.env.BACKEND_HOST || "http://localhost:8000";
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

function getVersion() {
    if (devMode) {
        console.log('Dev mode enabled - using dev version');
        return '9.9.9.9';
    }

    try {
        const result = execSync('git tag --sort=-version:refname', { encoding: 'utf8', stdio: 'pipe' });
        const tags = result.trim().split('\n').filter(tag => tag.trim());
        return tags.length > 0 ? tags[0].trim() : '9.9.9.9';
    } catch {
        console.log('Could not get git tags, using dev mode - please check YOUR GIT CONFIG');
        return '9.9.9.9';
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
            config.backendHost = backendHost;
            fs.writeFileSync(configPath, JSON.stringify(config, null, 2));


            console.log(`backendHost: ${backendHost}`);
            console.log(`Updated ${configPath}`);
        } else {
            console.log('BACKEND_HOST environment variable found, no changes made');
        }
    } else {
        const version = getVersion();

        config.backendHost = backendHost;
        config.version = version;

        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

        const packageUpdated = updatePackageJson(version, projectRoot);

        // LOGGING
        console.log(`Config updated${devMode ? ' (DEV MODE)' : ''}:`);
        console.log(`backendHost: ${backendHost}`);
        console.log(`version: ${version}`);
        if (packageUpdated) {
            console.log(`Updated package.json`);
        }
        console.log(`Updated ${configPath}`);
    }

} catch (error) {
    console.error('Error during setup:', error.message);
    console.log('Continuing with build...');
}