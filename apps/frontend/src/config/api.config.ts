/**
 * Centralized API Configuration
 * 
 * This file provides a single source of truth for all API endpoint configuration.
 * It handles the base URL, API prefix, and authentication settings.
 */

// Get configuration from environment variables or use defaults
const API_HOST = import.meta.env.VITE_API_HOST || 'localhost';
const API_PORT = import.meta.env.VITE_API_PORT || '8885';
const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL || 'http';
// NOTE: MCPO appends the server name to the path prefix
// So with --path-prefix "/api/mcpo/", endpoints are at "/api/mcpo/taskwarrior/"
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/mcpo/taskwarrior';
const API_KEY = import.meta.env.VITE_MCPO_API_KEY || 'taskwarrior-secret-key';

// Build the base URL
const BASE_URL = import.meta.env.VITE_API_URL || `${API_PROTOCOL}://${API_HOST}:${API_PORT}`;

/**
 * API Configuration object
 * Provides all necessary configuration for API communication
 */
export const apiConfig = {
  /**
   * Base URL for the API (includes protocol, host, and port)
   * e.g., "http://localhost:8885"
   */
  baseUrl: BASE_URL,

  /**
   * API prefix path
   * e.g., "/api/mcpo"
   */
  prefix: API_PREFIX,

  /**
   * Full API URL (base + prefix)
   * e.g., "http://localhost:8885/api/mcpo"
   */
  apiUrl: `${BASE_URL}${API_PREFIX}`,

  /**
   * API Key for authentication
   */
  apiKey: API_KEY,

  /**
   * Headers to include in all API requests
   */
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
  },

  /**
   * Get the full URL for a specific endpoint
   * @param endpoint - The endpoint path (e.g., "/list_tasks")
   * @returns The full URL (e.g., "http://localhost:8885/api/mcpo/list_tasks")
   */
  getEndpointUrl(endpoint: string): string {
    // Ensure endpoint starts with /
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${this.apiUrl}${normalizedEndpoint}`;
  },

  /**
   * Get URL for API documentation
   */
  get docsUrl(): string {
    return `${this.apiUrl}/docs`;
  },

  /**
   * Get URL for OpenAPI specification
   */
  get openApiUrl(): string {
    return `${this.apiUrl}/openapi.json`;
  },

  /**
   * Check if API is configured with a prefix
   */
  get hasPrefix(): boolean {
    return this.prefix !== '' && this.prefix !== '/';
  },

  /**
   * Get display-friendly API information
   */
  get displayInfo() {
    return {
      host: API_HOST,
      port: API_PORT,
      prefix: this.prefix,
      fullUrl: this.apiUrl,
      docsUrl: this.docsUrl,
    };
  },
};

/**
 * Helper function to make API requests with proper configuration
 */
export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = apiConfig.getEndpointUrl(endpoint);
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...apiConfig.headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * Helper function for MCPO tool invocation
 */
export async function invokeMCPOTool<T = any>(
  toolName: string,
  params?: any
): Promise<T> {
  return apiRequest<T>(`/${toolName}`, {
    method: 'POST',
    body: JSON.stringify( params || {}),
  });
}

// Export as default for convenience
export default apiConfig;