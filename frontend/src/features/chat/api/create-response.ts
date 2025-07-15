import { api } from "@/lib/api-client";

type ChatResponse = {
  session_id: string;
  user_query: string;
};

export const createResponse = async ({
  session_id,
  user_query,
}: ChatResponse) => {
  try {
    if (!session_id || !user_query) {
      throw new Error("Session ID and user query are required.");
    }
    const response = await api.post("/create/chat", {
      session_id: session_id,
      query: user_query,
    });
    return response.data;
  } catch (error) {
    console.error("Error in createResponse:", error);
  }
};
