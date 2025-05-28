let backendHostCache: null = null;

export async function getBackendHost() {
  if (backendHostCache) return backendHostCache;

  if (typeof window === 'undefined') {
    const fs = await import('fs/promises');
    const data = await fs.readFile('./public/skyeconfig.json', 'utf-8');
    const json = JSON.parse(data);
    backendHostCache = json.backendHost;
  } else {
    const res = await fetch('/skyeconfig.json');
    if (!res.ok) throw new Error('Failed to load skyeconfig.json');
    const json = await res.json();
    backendHostCache = json.backendHost;
  }

  if (!backendHostCache) {
    throw new Error('backendHost is missing in skyeconfig.json');
  }
  return backendHostCache;
}
