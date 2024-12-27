import axios from 'axios';

export const login = () => {
  window.location.href = 'http://127.0.0.1:8000/auth/login';
};

export const logout = async () => {
  await axios.post('http://127.0.0.1:8000/auth/logout');
  window.location.href = '/';
};