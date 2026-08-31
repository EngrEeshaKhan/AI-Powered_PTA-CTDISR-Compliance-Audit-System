import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { login as loginRequest } from "../services/auth.service";

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem("pta_user") || "null");
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser);
  const [token, setToken] = useState(
    () => localStorage.getItem("pta_access_token") || null
  );

  useEffect(() => {
    const handleExpired = () => {
      setUser(null);
      setToken(null);
    };
    window.addEventListener("pta-auth-expired", handleExpired);
    return () => window.removeEventListener("pta-auth-expired", handleExpired);
  }, []);

  async function signIn(username, password) {
    const result = await loginRequest(username, password);
    localStorage.setItem("pta_access_token", result.access_token);
    localStorage.setItem(
      "pta_user",
      JSON.stringify({
        username: result.username,
        role: result.role,
      })
    );
    setToken(result.access_token);
    setUser({ username: result.username, role: result.role });
    return result;
  }

  function signOut() {
    localStorage.removeItem("pta_access_token");
    localStorage.removeItem("pta_user");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isAdmin: user?.role === "admin",
      isAuditor: user?.role === "auditor",
      signIn,
      signOut,
    }),
    [user, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}