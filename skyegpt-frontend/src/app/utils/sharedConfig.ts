let configCache: { backendHost: string; version: string } | null = null;

async function loadConfigFile() {
  if (typeof window === 'undefined') {
    // SERVER-SIDE TODO - PERHAPS REFACTOR THIS
    const fs = await import('fs/promises');
    const data = await fs.readFile('./public/skyeconfig.json', 'utf-8');
    return JSON.parse(data);
  } else {
    // CLIENT-SIDE
    const res = await fetch('/skyeconfig.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }
}

export async function getConfig() {
  if (configCache) return configCache;

  const loadedConfig = await loadConfigFile();

  if (!loadedConfig.backendHost) {
    throw new Error('backendHost missing from config file - run setup-config script');
  }

  if (!loadedConfig.version) {
    throw new Error('version missing from config file - run setup-config script');
  }

  configCache = {
    backendHost: loadedConfig.backendHost,
    version: loadedConfig.version
  };

  return configCache;
}

export async function getBackendHost() {
  const config = await getConfig();
  return config.backendHost;
}

export async function getVersion() {
  const config = await getConfig();
  return config.version;
}