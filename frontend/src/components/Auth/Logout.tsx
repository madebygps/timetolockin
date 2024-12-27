import React from 'react';
import axios from 'axios';

const Logout: React.FC = () => {
  const handleLogout = async () => {
    await axios.post('http://127.0.0.1:8000/auth/logout');
    window.location.href = '/';
  };

  return (
    <div>
      <h2>Logout</h2>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default Logout;