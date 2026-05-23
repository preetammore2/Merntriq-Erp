const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const appConfig = {
  apiBaseUrl,
  apiDocsUrl: apiBaseUrl.replace("/api/v1", "/api/docs/"),
  apiHealthUrl: `${apiBaseUrl}/health/`
};
