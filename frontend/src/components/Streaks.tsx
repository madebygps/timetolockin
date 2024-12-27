import React from 'react';

const Streaks: React.FC = () => {
  // Sample data for streaks
  const streaks = [
    { date: '2023-10-01', completed: true },
    { date: '2023-10-02', completed: true },
    { date: '2023-10-03', completed: false },
    // Add more streak data as needed
  ];

  return (
    <div>
      <h2>Streaks Information</h2>
      <ul>
        {streaks.map((streak, index) => (
          <li key={index}>
            {streak.date}: {streak.completed ? 'Completed' : 'Missed'}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Streaks;