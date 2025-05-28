import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

describe('env.config.mjs', () => {
  let originalEnv: string | undefined;
  const configPath = path.join(process.cwd(), 'public/skyeconfig.json');
  
  beforeEach(() => {
    originalEnv = process.env.BACKEND_HOST_URL;
    if (fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
  });
  
  afterEach(() => {
    if (originalEnv) {
      process.env.BACKEND_HOST_URL = originalEnv;
    } else {
      delete process.env.BACKEND_HOST_URL;
    }
    if (fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
  });

  it('should create config with custom backend host from env var', () => {
    process.env.BACKEND_HOST_URL = 'http://custom-backend:9000';
    console.log('Using custom backend host:', process.env.BACKEND_HOST_URL);
    
    execSync('node env.config.mjs', { encoding: 'utf8' });
    
    expect(fs.existsSync(configPath)).toBe(true);
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://custom-backend:9000');
    console.log('Config created with backend host:', config.backendHost);
  });

  it('should create config with default backend host when no env var', () => {
    delete process.env.BACKEND_HOST_URL;
    
    execSync('node env.config.mjs', { encoding: 'utf8' });
    
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    expect(config.backendHost).toBe('http://localhost:8000');
    console.log('Config created with default backend host:', config.backendHost);
  });
});