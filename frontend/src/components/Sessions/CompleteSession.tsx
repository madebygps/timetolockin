import React, { useState } from 'react';
import axios from 'axios';

const CompleteSession: React.FC = () => {
  const [sessionId, setSessionId] = useState('');
  const [userId, setUserId] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/sessions/complete', { session_id: sessionId, user_id: userId });
      alert(response.data.message);
    } catch (error) {
      alert('Error completing session');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Complete Session</h2>
      <input type="text" value={sessionId} onChange={(e) => setSessionId(e.target.value)} placeholder="Session ID" required />
      <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="User ID" required />
      <button type="submit">Complete Session</button>
    </form>
  );
};

export default CompleteSession;