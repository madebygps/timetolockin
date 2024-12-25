<template>
  <div>
    <button @click="login">Login with GitHub</button>
  </div>
</template>

<script>
export default {
  methods: {
    login() {
      // Redirect to the backend for GitHub OAuth
      window.location.href = 'http://127.0.0.1:8000/auth/login';
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
