import React, { useState } from 'react';
import axios from 'axios';

const GetSessionState: React.FC = () => {
  const [sessionId, setSessionId] = useState('');
  const [sessionState, setSessionState] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.get(`http://127.0.0.1:8000/sessions/${sessionId}`);
      setSessionState(response.data);
    } catch (error) {
      alert('Error fetching session state');
    }
  };

  return (
    <div>
      <h2>Get Session State</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" value={sessionId} onChange={(e) => setSessionId(e.target.value)} placeholder="Session ID" required />
        <button type="submit">Get State</button>
      </form>
      {sessionState && (
        <div>
          <h3>Session State</h3>
          <pre>{JSON.stringify(sessionState, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default GetSessionState;