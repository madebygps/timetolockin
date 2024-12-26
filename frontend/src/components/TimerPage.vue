<template>
    <div class="timer-page">
      <h2>Pomodoro Timer</h2>
      <p>Pomodoro: {{ currentPomodoro }} / {{ totalPomodoros }}</p>
      <p>{{ timerDisplay }}</p>
      <button @click="startPomodoro" :disabled="isRunning">Start</button>
      <button @click="pausePomodoro" :disabled="!isRunning">Pause</button>
      <button @click="resetPomodoro">Reset</button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      sessionId: {
        type: String,
        required: true,
      },
      userId: {
        type: String,
        required: true,
      },
      totalPomodoros: {
        type: Number,
        default: 4,
      },
    },
    data() {
      return {
        currentPomodoro: 1,
        timer: 25 * 60, // 25 minutes in seconds
        isRunning: false,
        timerInterval: null,
      };
    },
    computed: {
      timerDisplay() {
        const minutes = Math.floor(this.timer / 60);
        const seconds = this.timer % 60;
        return `${minutes}:${seconds.toString().padStart(2, "0")}`;
      },
    },
    methods: {
      startPomodoro() {
        if (this.currentPomodoro > this.totalPomodoros) {
          this.$emit("sessionComplete");
          return;
        }
        this.isRunning = true;
        this.timerInterval = setInterval(() => {
          if (this.timer > 0) {
            this.timer--;
          } else {
            clearInterval(this.timerInterval);
            this.timer = 5 * 60; // Break for 5 minutes
            this.isRunning = false;
  
            if (this.currentPomodoro === this.totalPomodoros) {
              alert("Session complete! Great job!");
              this.$emit("sessionComplete");
            } else {
              alert("Take a short break!");
              this.currentPomodoro++;
            }
          }
        }, 1000);
      },
      pausePomodoro() {
        this.isRunning = false;
        clearInterval(this.timerInterval);
      },
      resetPomodoro() {
        this.pausePomodoro();
        this.timer = 25 * 60;
      },
    },
    beforeUnmount() {
      clearInterval(this.timerInterval);
    },
  };
  </script>
  
  <style scoped>
  .timer-page {
    text-align: center;
    margin: 20px;
  }
  
  button {
    margin: 10px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
  }
  </style>
  