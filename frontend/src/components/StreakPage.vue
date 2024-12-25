<template>
  <div class="streak">
    <h1>Your Streak</h1>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <p>Current Streak: {{ streakData.streak }} days</p>
      <p>Longest Streak: {{ streakData.longest_streak }} days</p>
      <button @click="logout">Log Out</button>
    </div>
  </div>
</template>

<script>
import apiClient from "../api";

export default {
  data() {
    return {
      streakData: null,
      loading: true,
      error: null,
    };
  },
  methods: {
    fetchStreak() {
      apiClient
        .get("/streak")
        .then((response) => {
          this.streakData = response.data;
        })
        .catch(() => {
          this.error = "Failed to fetch streak data.";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    logout() {
      apiClient.post("/auth/logout").then(() => {
        window.location.href = "/";
      });
    },
  },
  mounted() {
    this.fetchStreak();
  },
};
</script>

<style>
.streak {
  text-align: center;
  margin-top: 50px;
}
button {
  background-color: #dc3545;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
