import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Auth/Login';
import Logout from './components/Auth/Logout';
import CreateSession from './components/Sessions/CreateSession';
import CompleteSession from './components/Sessions/CompleteSession';
import UpdatePomodoro from './components/Sessions/UpdatePomodoro';
import StartSession from './components/Sessions/StartSession';
import GetSessionState from './components/Sessions/GetSessionState';
import Streaks from './components/Streaks';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/create-session" element={<CreateSession />} />
        <Route path="/complete-session" element={<CompleteSession />} />
        <Route path="/update-pomodoro" element={<UpdatePomodoro />} />
        <Route path="/start-session" element={<StartSession />} />
        <Route path="/get-session-state" element={<GetSessionState />} />
        <Route path="/streaks" element={<Streaks />} />
      </Routes>
    </Router>
  );
};

export default App;