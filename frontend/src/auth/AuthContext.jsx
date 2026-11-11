import { createContext, useContext, useEffect, useState } from "react";
import { fetchMe, loginAccount, logoutAccount, registerAccount } from "../api/auth.js";

const TOKEN_KEY = "doxami_access_token";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(TOKEN_KEY)));

  useEffect(() => {
    let cancelled = false;
    async function hydrate() {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const me = await fetchMe(token);
        if (!cancelled) setUser(me);
      } catch {
        if (!cancelled) {
          localStorage.removeItem(TOKEN_KEY);
          setToken("");
          setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    hydrate();
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function register(payload) {
    const result = await registerAccount(payload);
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    return result;
  }

  async function login(payload) {
    const result = await loginAccount(payload);
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    return result;
  }

  function applyToken(accessToken) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    setToken(accessToken);
  }

  async function logout() {
    if (token) {
      try {
        await logoutAccount(token);
      } catch {
        /* client still clears local session */
      }
    }
    localStorage.removeItem(TOKEN_KEY);
    setToken("");
    setUser(null);
  }

  const value = {
    token,
    user,
    loading,
    isAuthenticated: Boolean(user),
    register,
    login,
    logout,
    applyToken,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
