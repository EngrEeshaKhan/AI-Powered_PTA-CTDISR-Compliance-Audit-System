import api from "./api";

export async function getDashboardStatistics() {
  const { data } = await api.get("/dashboard/statistics");
  return data;
}