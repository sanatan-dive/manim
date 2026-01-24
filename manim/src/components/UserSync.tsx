import { useAuth, useUser } from "@clerk/clerk-react";
import { useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function UserSync() {
  const { getToken, isSignedIn } = useAuth();
  const { user } = useUser();

  useEffect(() => {
    const syncUser = async () => {
      if (isSignedIn && user) {
        try {
          const token = await getToken();
          await fetch(`${API_URL}/users/sync`, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
        } catch (err) {
          console.error("Failed to sync user", err);
        }
      }
    };
    syncUser();
  }, [isSignedIn, user, getToken]);

  return null;
}
