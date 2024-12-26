<template>
  <div class="pomodoro-page">
    <h1>Pomodoro Session</h1>
    <p>Intention: {{ intention }}</p>

    <!-- Timer Component -->
    <Timer
      :sessionId="sessionId"
      :userId="userId"
      :totalPomodoros="totalPomodoros"
      @sessionComplete="handleSessionComplete"
    />

    <button @click="goToStreaks">View Streaks</button>
  </div>
</template>

<script>
import Timer from "@/components/TimerPage.vue";

export default {
  components: { Timer },
  data() {
    return {
      sessionId: "", // The session ID returned from the backend
      userId: "", // The logged-in user's ID
      totalPomodoros: 4, // Default number of Pomodoros in the session
      intention: "Focus on completing the project", // Intention for the session
    };
  },
  mounted() {
  // Check if userId exists in Vuex
  if (!this.$store.getters.getUserId) {
    console.log("No userId in Vuex, redirecting to login");
    alert("Please log in first.");
    this.$router.push("/");
  } else {
    console.log("User ID found:", this.$store.getters.getUserId);
    this.startSession();
  }
},

  methods: {
    async startSession() {
      try {
        const response = await this.$axios.post("http://127.0.0.1:8000/sessions/start", {
          repo: "your-repo-name", // Replace with actual repo if needed
          intention: this.intention,
        });
        this.sessionId = response.data.session_id;
      } catch (error) {
        console.error("Failed to start session:", error.response?.data || error.message);
        alert("Error starting session. Please try again.");
      }
    },
    handleSessionComplete() {
      alert("Pomodoro session completed! Great job!");
      // Optionally redirect to streaks or another page
      this.goToStreaks();
    },
    goToStreaks() {
      this.$router.push("/streaks");
    },
  },
};
</script>

<style scoped>
.pomodoro-page {
  text-align: center;
  margin: 20px;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>
