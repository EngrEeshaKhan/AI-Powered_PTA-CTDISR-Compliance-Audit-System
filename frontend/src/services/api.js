import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("pta_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("pta_access_token");
      localStorage.removeItem("pta_user");
      window.dispatchEvent(new Event("pta-auth-expired"));
    }
    return Promise.reject(error);
  }
);

export default api;

export function getApiError(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((x) => x.msg).join(", ");
  return error?.message || fallback;
}