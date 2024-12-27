import axios from 'axios';

export const createSession = async (data: any) => {
  return await axios.post('http://127.0.0.1:8000/sessions/create', data);
};

export const completeSession = async (sessionId: string, userId: string) => {
  return await axios.post('http://127.0.0.1:8000/sessions/complete', { session_id: sessionId, user_id: userId });
};

export const updatePomodoro = async (sessionId: string, userId: string) => {
  return await axios.post('http://127.0.0.1:8000/sessions/update', { session_id: sessionId, user_id: userId });
};

export const startSession = async (sessionId: string) => {
  return await axios.post('http://127.0.0.1:8000/sessions/start', { session_id: sessionId });
};

export const getSessionState = async (sessionId: string) => {
  return await axios.get(`http://127.0.0.1:8000/sessions/${sessionId}`);
};