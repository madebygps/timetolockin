<template>
  <div class="streaks-view">
    <h1>Your Weekly Streaks</h1>
    <div class="week-calendar">
      <div 
        v-for="(day, index) in weekDays" 
        :key="index" 
        class="day"
        :class="{ completed: isDayCompleted(day) }"
      >
        <span class="day-name">{{ day.name }}</span>
        <span class="status">{{ isDayCompleted(day) ? '✔️' : '❌' }}</span>
      </div>
    </div>
    <button @click="goBack">Back to Pomodoro</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userId: "", // User ID retrieved from session or global store
      completedDays: [], // Array of completed days
      weekDays: [
        { name: "Sunday", date: null },
        { name: "Monday", date: null },
        { name: "Tuesday", date: null },
        { name: "Wednesday", date: null },
        { name: "Thursday", date: null },
        { name: "Friday", date: null },
        { name: "Saturday", date: null },
      ],
    };
  },
  async mounted() {
    // Set dates for the current week
    this.initializeWeekDates();
    // Fetch streak data from the backend
    await this.fetchStreakData();
  },
  methods: {
    initializeWeekDates() {
      const today = new Date();
      const dayOfWeek = today.getDay();

      // Calculate the start of the week (Sunday)
      const startOfWeek = new Date(
        today.getFullYear(),
        today.getMonth(),
        today.getDate() - dayOfWeek
      );

      // Assign dates to each day in the week
      this.weekDays.forEach((day, index) => {
        const date = new Date(
          startOfWeek.getFullYear(),
          startOfWeek.getMonth(),
          startOfWeek.getDate() + index
        );
        day.date = date.toISOString().split("T")[0]; // Format as YYYY-MM-DD
      });
    },
    async fetchStreakData() {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/streaks/${this.userId}`
        );
        this.completedDays = response.data.completed_days; // Expected: ["2024-12-23", "2024-12-25"]
      } catch (error) {
        console.error("Failed to fetch streak data:", error);
        alert("Error fetching streak data.");
      }
    },
    isDayCompleted(day) {
      return this.completedDays.includes(day.date);
    },
    goBack() {
      this.$router.push("/pomodoro");
    },
  },
};
</script>

<style scoped>
.streaks-view {
  text-align: center;
  margin: 20px;
}

.week-calendar {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border: 1px solid #ccc;
  border-radius: 10px;
  background-color: #f9f9f9;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.day.completed {
  background-color: #4caf50;
  color: white;
}

.day-name {
  font-size: 16px;
  font-weight: bold;
}

.status {
  font-size: 24px;
  margin-top: 10px;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>
