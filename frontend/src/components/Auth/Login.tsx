import React from 'react';

const Login: React.FC = () => {
  const handleLogin = () => {
    window.location.href = 'http://127.0.0.1:8000/auth/login';
  };

  return (
    <div>
      <h2>Login</h2>
      <button onClick={handleLogin}>Login with GitHub</button>
    </div>
  );
};

export default Login;