<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Tenno Login</h1>
        <p class="auth-subtitle">Access your Cephalon console</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            placeholder="tenno@warframe.com"
            :disabled="loading"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="Enter your password"
            :disabled="loading"
            class="form-input"
          />
        </div>

        <div v-if="error" class="message message-error">
          {{ error }}
        </div>

        <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading">
          <span v-if="loading">Authenticating...</span>
          <span v-else>Login</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>No account? <RouterLink to="/register" class="auth-link">Create one</RouterLink></p>
        <RouterLink to="/" class="back-link">← Back to Home</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";

const router = useRouter();
const { login, user, isAdmin } = useAuth();

const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    await login(email.value, password.value);
    
    // Login successful, redirect based on user role
    if (isAdmin.value) {
      router.push("/admin");
    } else {
      router.push("/");
    }
  } catch (err: any) {
    error.value = err.message || "An error occurred during login";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  padding: var(--space-8);
}

.auth-card {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-10);
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-sm);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.auth-title {
  color: var(--accent);
  font-size: var(--text-3xl);
  font-weight: bold;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: var(--space-2);
}

.auth-subtitle {
  color: var(--text-primary);
  opacity: 0.7;
  font-size: var(--text-body);
}

.auth-form {
  margin-bottom: var(--space-8);
}

.form-group {
  margin-bottom: var(--space-6);
}

.form-group label {
  display: block;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  font-size: var(--text-body);
}

.auth-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: bold;
}

.auth-link:hover {
  color: var(--accent-hover);
}

.back-link {
  color: var(--text-primary);
  opacity: 0.6;
  text-decoration: none;
  font-size: var(--text-base);
}

.back-link:hover {
  opacity: 0.8;
}
</style>