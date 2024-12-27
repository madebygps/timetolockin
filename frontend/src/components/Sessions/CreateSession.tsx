import React, { useState } from 'react';
import axios from 'axios';

const CreateSession: React.FC = () => {
  const [repo, setRepo] = useState('');
  const [intention, setIntention] = useState('');
  const [totalPomodoros, setTotalPomodoros] = useState(1);
  const [pomodoroLength, setPomodoroLength] = useState(25);
  const [breakLength, setBreakLength] = useState(2);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/sessions/create', {
        repo,
        intention,
        total_pomodoros: totalPomodoros,
        pomodoro_length: pomodoroLength,
        break_length: breakLength,
      });
      alert(response.data.message);
    } catch (error) {
      alert('Error creating session');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Create Session</h2>
      <input type="text" value={repo} onChange={(e) => setRepo(e.target.value)} placeholder="Repository" required />
      <input type="text" value={intention} onChange={(e) => setIntention(e.target.value)} placeholder="Intention" required />
      <input type="number" value={totalPomodoros} onChange={(e) => setTotalPomodoros(Number(e.target.value))} placeholder="Total Pomodoros" min="1" max="10" required />
      <input type="number" value={pomodoroLength} onChange={(e) => setPomodoroLength(Number(e.target.value))} placeholder="Pomodoro Length" min="25" max="60" required />
      <input type="number" value={breakLength} onChange={(e) => setBreakLength(Number(e.target.value))} placeholder="Break Length" min="2" max="5" required />
      <button type="submit">Create Session</button>
    </form>
  );
};

export default CreateSession;