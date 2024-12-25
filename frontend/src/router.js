import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from './components/LoginPage.vue';
import PomodoroPage from './components/PomodoroPage.vue';
import StreakPage from './components/StreakPage.vue';

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/pomodoro',
    name: 'Pomodoro',
    component: PomodoroPage,
  },
  {
    path: '/streaks',
    name: 'Streaks',
    component: StreakPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;