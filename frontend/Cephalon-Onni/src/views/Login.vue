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
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="auth-button" :disabled="loading">
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
const { fetchUser } = useAuth();

const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Login failed");
    }

    // Login successful, update user state and redirect
    await fetchUser();
    const user = await response.json();
    if (user.role === "admin" || user.role === "administrator") {
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
  background: #02050a;
  padding: 2rem;
}

.auth-card {
  background: #050b16;
  border: 1px solid #1b2a3a;
  border-radius: 8px;
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-title {
  color: #38bdf8;
  font-size: 1.8rem;
  font-weight: bold;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.auth-subtitle {
  color: #c9e5ff;
  opacity: 0.7;
  font-size: 0.9rem;
}

.auth-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: #c9e5ff;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  background: #08121f;
  border: 1px solid #1b2a3a;
  border-radius: 4px;
  padding: 0.75rem;
  color: #c9e5ff;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #38bdf8;
}

.form-group input:disabled {
  opacity: 0.5;
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.auth-button {
  width: 100%;
  background: #38bdf8;
  color: #021019;
  border: none;
  border-radius: 4px;
  padding: 0.875rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.auth-button:hover:not(:disabled) {
  background: #0ea5e9;
}

.auth-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  border-top: 1px solid #1b2a3a;
  padding-top: 1.5rem;
}

.auth-footer p {
  color: #c9e5ff;
  opacity: 0.7;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.auth-link {
  color: #38bdf8;
  text-decoration: none;
  font-weight: bold;
}

.auth-link:hover {
  color: #0ea5e9;
}

.back-link {
  color: #c9e5ff;
  opacity: 0.6;
  text-decoration: none;
  font-size: 0.8rem;
}

.back-link:hover {
  opacity: 0.8;
}
</style>