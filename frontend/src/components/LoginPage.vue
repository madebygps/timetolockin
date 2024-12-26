<template>
  <div>
    <button @click="login">Login with GitHub</button>
  </div>
</template>

<script>
export default {
  methods: {
    login() {
  // Redirect to backend for GitHub OAuth
  window.location.href = "http://127.0.0.1:8000/auth/login";
},
async handleAuthCallback() {
  try {
    const response = await this.$axios.get("http://127.0.0.1:8000/auth/callback");
    const { user_id, access_token } = response.data;

    // Save to Vuex
    console.log("User ID:", user_id); // Log userId for debugging
    this.$store.dispatch("saveUserId", user_id);
    this.$store.dispatch("saveAccessToken", access_token);

    // Redirect to Pomodoro page
    this.$router.push("/pomodoro");
  } catch (error) {
    console.error("Error handling auth callback:", error);
  }
},

  },
};
</script>

<style>
button {
  background-color: #dc3545;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>