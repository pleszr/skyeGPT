import { writeFileSync, readFileSync } from 'fs';
import { execSync } from 'child_process';

try {
  const packageJson = JSON.parse(readFileSync('package.json', 'utf8'));
  
  // Get the latest tag from git to set as the version
  const baseVersion = execSync('git describe --tags --abbrev=0', { encoding: 'utf8' }).trim();
  
  packageJson.version = baseVersion;
  writeFileSync('package.json', JSON.stringify(packageJson, null, 2));
  
  console.log(`Version updated to: ${baseVersion}`);
} catch (error) {
  console.error('Error setting version:', error.message);
  process.exit(1);
}