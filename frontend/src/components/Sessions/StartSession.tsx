import React, { useState } from 'react';
import axios from 'axios';

const StartSession: React.FC = () => {
  const [sessionId, setSessionId] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/sessions/start', { session_id: sessionId });
      alert(response.data.message);
    } catch (error) {
      alert('Error starting session');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Start Session</h2>
      <input type="text" value={sessionId} onChange={(e) => setSessionId(e.target.value)} placeholder="Session ID" required />
      <button type="submit">Start Session</button>
    </form>
  );
};

export default StartSession;