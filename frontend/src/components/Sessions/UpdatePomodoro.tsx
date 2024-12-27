import React, { useState } from 'react';
import axios from 'axios';

const UpdatePomodoro: React.FC = () => {
  const [sessionId, setSessionId] = useState('');
  const [userId, setUserId] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/sessions/update', { session_id: sessionId, user_id: userId });
      alert(response.data.message);
    } catch (error) {
      alert('Error updating Pomodoro');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Update Pomodoro</h2>
      <input type="text" value={sessionId} onChange={(e) => setSessionId(e.target.value)} placeholder="Session ID" required />
      <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="User ID" required />
      <button type="submit">Update Pomodoro</button>
    </form>
  );
};

export default UpdatePomodoro;