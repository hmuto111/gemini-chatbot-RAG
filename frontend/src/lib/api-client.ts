import Axios from "axios";

export const api = Axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  responseEncoding: "utf8",
  maxRedirects: 5,
});
