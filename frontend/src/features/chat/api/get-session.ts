import { api } from "@/lib/api-client";

export const getSession = async () => {
  try {
    const response = await api.get("/create/session");
    return response.data;
  } catch (error) {
    console.error("Error fetching session:", error);
    throw error;
  }
};
