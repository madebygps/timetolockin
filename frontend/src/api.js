import axios from "axios";


const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000", // FastAPI backend URL
  withCredentials: true, // To handle cookies/session
  timeout: 5000,
});

export default apiClient;
