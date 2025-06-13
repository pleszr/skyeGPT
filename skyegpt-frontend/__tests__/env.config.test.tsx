import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

describe('prebuild.mjs', () => {
  let originalEnv: string | undefined;
  let originalDevMode: string | undefined;
  const configPath = path.join(process.cwd(), 'public/skyeconfig.json');
  const packagePath = path.join(process.cwd(), 'package.json');
  let originalPackageJson: string;

  beforeEach(() => {
    originalEnv = process.env.BACKEND_HOST;
    originalDevMode = process.env.DEV_MODE;

    originalPackageJson = fs.readFileSync(packagePath, 'utf8');

    if (fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
  });

  afterEach(() => {
    if (originalEnv) {
      process.env.BACKEND_HOST = originalEnv;
    } else {
      delete process.env.BACKEND_HOST;
    }

    if (originalDevMode) {
      process.env.DEV_MODE = originalDevMode;
    } else {
      delete process.env.DEV_MODE;
    }

    fs.writeFileSync(packagePath, originalPackageJson);

    if (fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
  });

  it('should create config with custom backend host from env var', () => {
    process.env.BACKEND_HOST = 'http://custom-backend:9000';

    execSync('node prebuild.mjs', { encoding: 'utf8' });

    expect(fs.existsSync(configPath)).toBe(true);
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://custom-backend:9000');
    expect(config.version).toBeDefined();
  });

  it('should create config with default backend host when no env var', () => {
    delete process.env.BACKEND_HOST;

    execSync('node prebuild.mjs', { encoding: 'utf8' });

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://localhost:8000');
    expect(config.version).toBeDefined();
  });

  it('should use dev version when --dev flag is passed', () => {
    process.env.BACKEND_HOST = 'http://test-backend:8000';

    execSync('node prebuild.mjs --dev', { encoding: 'utf8' });

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://test-backend:8000');
    expect(config.version).toBe('9.9.9.9');
  });

  it('should use dev version when DEV_MODE env var is true', () => {
    process.env.DEV_MODE = 'true';
    process.env.BACKEND_HOST = 'http://test-backend:8000';

    execSync('node prebuild.mjs', { encoding: 'utf8' });

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://test-backend:8000');
    expect(config.version).toBe('9.9.9.9');
  });

  it('should only update backend host in setenv-only mode', () => {
    const initialConfig = {
      backendHost: 'http://old-backend:8000',
      version: '1.0.0'
    };
    fs.writeFileSync(configPath, JSON.stringify(initialConfig, null, 2));

    process.env.BACKEND_HOST = 'http://new-backend:9000';

    execSync('node prebuild.mjs --setenv-only', { encoding: 'utf8' });

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://new-backend:9000');
    expect(config.version).toBe('1.0.0');
  });

  it('should not update anything in setenv-only mode when no BACKEND_HOST env var', () => {
    const initialConfig = {
      backendHost: 'http://old-backend:8000',
      version: '1.0.0'
    };
    fs.writeFileSync(configPath, JSON.stringify(initialConfig, null, 2));

    delete process.env.BACKEND_HOST;

    execSync('node prebuild.mjs --setenv-only', { encoding: 'utf8' });

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://old-backend:8000');
    expect(config.version).toBe('1.0.0');
  });

  it('should update package.json version in normal mode', () => {
    process.env.BACKEND_HOST = 'http://test-backend:8000';

    execSync('node prebuild.mjs --dev', { encoding: 'utf8' });

    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    expect(packageJson.version).toBe('9.9.9.9');
  });

  it('should not update package.json version in setenv-only mode', () => {
    process.env.BACKEND_HOST = 'http://test-backend:8000';
    const originalPackage = JSON.parse(originalPackageJson);

    execSync('node prebuild.mjs --setenv-only', { encoding: 'utf8' });

    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    expect(packageJson.version).toBe(originalPackage.version);
  });

  it('should preserve existing config properties when updating', () => {
    const initialConfig = {
      backendHost: 'http://old-backend:8000',
      version: '1.0.0',
      customProperty: 'should-be-preserved'
    };
    fs.writeFileSync(configPath, JSON.stringify(initialConfig, null, 2));

    process.env.BACKEND_HOST = 'http://new-backend:9000';

    execSync('node prebuild.mjs', { encoding: 'utf8' });

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://new-backend:9000');
    expect(config.version).toBeDefined();
    expect(config.customProperty).toBe('should-be-preserved');
  });
});