"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { AuthToken, verifyAuth } from "@/lib/auth";

interface AuthContextType {
  user: AuthToken | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: AuthToken | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthToken | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const verified = await verifyAuth();
      setUser(verified);
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
