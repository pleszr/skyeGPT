import { writeFileSync, readFileSync } from 'fs';
import { execSync } from 'child_process';

// Simple semver validation regex
// https://stackoverflow.com/questions/72900289/regex-for-semver
const SEMVER_REGEX = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;

function isValidSemver(version) {
  return SEMVER_REGEX.test(version);
}

try {
  const packageJson = JSON.parse(readFileSync('package.json', 'utf8'));
  
  // Get the latest tag from git to set as the version
  const baseVersion = execSync('git describe --tags --abbrev=0', { encoding: 'utf8' }).trim();
  
  // Validate semver format
  if (!isValidSemver(baseVersion)) {
    throw new Error(`Invalid SEMANTIC version format: "${baseVersion}". Expected format like "1.0.0"`);
  }
  
  packageJson.version = baseVersion;
  writeFileSync('package.json', JSON.stringify(packageJson, null, 2));
  
  console.log(`Version updated to: ${baseVersion}`);
} catch (error) {
  console.error('Error setting version:', error.stack);
  process.exit(1);
}