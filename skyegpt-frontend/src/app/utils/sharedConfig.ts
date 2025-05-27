let backendHostCache: string | null = null;

export async function getBackendHost(): Promise<string> {
  if (backendHostCache) return backendHostCache;

  const res = await fetch('/skyeconfig.json');
  if (!res.ok) throw new Error('Failed to load skyeconfig.json');
  const json = await res.json();
  backendHostCache = json.backendHost;
  if (!backendHostCache) {
    throw new Error('backendHost is missing in skyeconfig.json');
  }
  return backendHostCache;
}