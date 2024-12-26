import { createStore } from 'vuex';

const store = createStore({
  state: {
    userId: null, // Store user ID
    sessionId: null, // Store session ID
    accessToken: null, // Store access token
  },
  mutations: {
    setUserId(state, userId) {
      state.userId = userId;
    },
    setSessionId(state, sessionId) {
      state.sessionId = sessionId;
    },
    setAccessToken(state, accessToken) {
      state.accessToken = accessToken;
    },
  },
  actions: {
    saveUserId({ commit }, userId) {
      commit('setUserId', userId);
    },
    saveSessionId({ commit }, sessionId) {
      commit('setSessionId', sessionId);
    },
    saveAccessToken({ commit }, accessToken) {
      commit('setAccessToken', accessToken);
    },
  },
  getters: {
    getUserId: (state) => state.userId,
    getSessionId: (state) => state.sessionId,
    getAccessToken: (state) => state.accessToken,
  },
});

export default store;
