const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";
const LOOPBACK_HOSTS = new Set(["localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"]);

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}

function resolveApiBaseUrl() {
  const configuredBase = trimTrailingSlash(process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL);
  if (typeof window === "undefined") return configuredBase;

  try {
    const apiUrl = new URL(configuredBase);
    const pageHost = window.location.hostname;

    if (!process.env.NEXT_PUBLIC_API_BASE_URL && window.location.protocol === "https:" && LOOPBACK_HOSTS.has(apiUrl.hostname)) {
      return "/api/v1";
    }

    if (pageHost && !LOOPBACK_HOSTS.has(pageHost) && LOOPBACK_HOSTS.has(apiUrl.hostname)) {
      apiUrl.hostname = pageHost;
    }

    return trimTrailingSlash(apiUrl.toString());
  } catch {
    return configuredBase;
  }
}

const apiBaseUrl = resolveApiBaseUrl();

export const appConfig = {
  apiBaseUrl,
  apiDocsUrl: apiBaseUrl.replace("/api/v1", "/api/docs/"),
  apiHealthUrl: `${apiBaseUrl}/health/`
};
