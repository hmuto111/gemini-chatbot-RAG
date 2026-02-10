import { useEffect, useState } from "react";
import { getSession } from "../api/get-session";

export const useSession = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        if (sessionStorage.getItem("session_id")) {
          setSessionId(sessionStorage.getItem("session_id"));
        } else {
          const response = await getSession();
          setSessionId(response.session_id);
          sessionStorage.setItem("session_id", response.session_id);
        }
      } catch (error) {
        console.error("Error fetching session:", error);
      }
    };
    console.log("Fetching session...");
    fetchSession();
  }, []);

  return { sessionId };
};
