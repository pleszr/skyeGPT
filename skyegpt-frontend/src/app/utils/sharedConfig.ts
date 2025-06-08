let configCache: { backendHost?: string; version?: string } | null = null;

export async function getConfig() {
  if (configCache) return configCache;

  if (typeof window === 'undefined') {
    const fs = await import('fs/promises');
    const data = await fs.readFile('./public/skyeconfig.json', 'utf-8');
    const json = JSON.parse(data);
    configCache = json;
  } else {
    const res = await fetch('/skyeconfig.json');
    if (!res.ok) throw new Error('Failed to load skyeconfig.json');
    const json = await res.json();
    configCache = json;
  }

  if (!configCache || !configCache.backendHost) {
    throw new Error('backendHost is missing in skyeconfig.json');
  }
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
