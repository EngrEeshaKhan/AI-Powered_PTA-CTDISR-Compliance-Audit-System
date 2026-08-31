import api from "./api";

export async function login(username, password) {
  const { data } = await api.post("/auth/login", { username, password });
  return data;
}

export async function getUsers() {
  const { data } = await api.get("/auth/users");
  return data;
}

export async function createUser(payload) {
  const { data } = await api.post("/auth/users", payload);
  return data;
}