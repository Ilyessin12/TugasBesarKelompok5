/**
 * Centralized API client for making requests to the backend
 */

/**
 * Returns the appropriate base URL based on the environment
 */
const getBaseUrl = () => {
  return typeof window !== 'undefined' 
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
    : 'http://api:5000';
};

/**
 * API client methods for all endpoints
 */
export const API = {
  // Financial data
  getFinancialData: async (emiten: string, year?: string) => {
    try {
      // Build URL with optional year parameter
      let url = `${getBaseUrl()}/api/financial/${emiten}`;
      if (year) {
        url += `?year=${year}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.message || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Failed to fetch financial data:", error);
      throw error;
    }
  },
  
  // News data
  getNewsData: async (emiten: string, limit = 20, skip = 0) => {
    try {
      // Use the correct endpoint format with pagination parameters
      // string tren = 
      const response = await fetch(`${getBaseUrl()}/api/news/${emiten}?limit=${limit}&skip=${skip}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.error || errorData?.message || `API Error: ${response.status}`
        );
      }
      
      return await response.json();
    } catch (error) {
      console.error("Failed to fetch news data:", error);
      throw error;
    }
  },
  
  // News summary
  getNewsSummary: async (emiten: string, limit = 10, skip = 0) => {
    const response = await fetch(`${getBaseUrl()}/api/news/summary/${emiten}?limit=${limit}&skip=${skip}`);
    if (!response.ok) throw new Error('Failed to fetch news summary');
    return response.json();
  },
  
  // Stock data
  getStockData: async (emiten: string, period: string = 'all') => {
    const response = await fetch(`${getBaseUrl()}/api/stock/${emiten}?period=${period}`);
    if (!response.ok) throw new Error('Failed to fetch stock data');
    return response.json();
  },

  // Emiten news
  getEmitenNews: async (emiten: string) => {
    try {
      const response = await fetch(`/api/news/${emiten}`);
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Failed to fetch news data:", error);
      throw error;
    }
  },
};
