<template>
    <div>
      <h1>Start a Pomodoro</h1>
      <form @submit.prevent="startPomodoro">
        <label for="repo">GitHub Repo:</label>
        <input type="text" v-model="repo" id="repo" required />
  
        <label for="intention">Intention:</label>
        <input type="text" v-model="intention" id="intention" required />
  
        <button type="submit">Start Pomodoro</button>
      </form>
      <button @click="goToStreaks">View Streaks</button>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        repo: '',
        intention: '',
      };
    },
    methods: {
      async startPomodoro() {
        try {
          const response = await axios.post('http://127.0.0.1:8000/sessions/start', {
            repo: this.repo,
            intention: this.intention,
          });
          alert('Pomodoro started: ' + response.data.message);
        } catch (error) {
          console.error('Failed to start Pomodoro:', error);
        }
      },
      goToStreaks() {
        this.$router.push('/streaks');
      },
    },
  };
  </script>
  