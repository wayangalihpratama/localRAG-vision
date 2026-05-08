import axios from "axios";

const API_BASE_URL = "/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const ingestApi = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post("/ingest/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
  getStatus: async (taskId: string) => {
    return apiClient.get(`/ingest/status/${taskId}`);
  },
  listFiles: async () => {
    return apiClient.get("/ingest/files");
  },
};

export const chatApi = {
  // Note: For streaming, we still often use native fetch because of better
  // ReadStream support in browsers, but we can wrap it here for consistency.
  streamChat: async (query: string) => {
    return fetch(`${API_BASE_URL}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
  },
};

export default apiClient;
