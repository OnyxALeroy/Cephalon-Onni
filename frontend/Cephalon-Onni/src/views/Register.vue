<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Tenno Registration</h1>
        <p class="auth-subtitle">Join the Cephalon network</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            placeholder="TennoName"
            :disabled="loading"
            class="form-input"
          />
        </div>

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
            placeholder="Create a strong password"
            :disabled="loading"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            required
            placeholder="Confirm your password"
            :disabled="loading"
            class="form-input"
          />
        </div>

        <div v-if="error" class="message message-error">
          {{ error }}
        </div>

        <div v-if="success" class="message message-success">
          {{ success }}
        </div>

        <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading || !isFormValid">
          <span v-if="loading">Creating Account...</span>
          <span v-else>Register</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <RouterLink to="/login" class="auth-link">Login</RouterLink></p>
        <RouterLink to="/" class="back-link">← Back to Home</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";

const router = useRouter();
const { register, login, isAdmin } = useAuth();

const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");

const isFormValid = computed(() => {
  return (
    username.value.trim() &&
    email.value.trim() &&
    password.value.length >= 6 &&
    password.value === confirmPassword.value
  );
});

async function handleRegister() {
  if (!isFormValid.value) {
    error.value = "Please fill all fields correctly";
    return;
  }

  loading.value = true;
  error.value = "";
  success.value = "";

  try {
    await register(username.value.trim(), email.value.trim(), password.value);
    
    // Registration successful
    success.value = "Account created successfully! Logging you in...";
    
    // Auto-login after successful registration
    setTimeout(async () => {
      try {
        await login(email.value.trim(), password.value);
        
        // Login successful, redirect based on user role
        if (isAdmin.value) {
          router.push("/admin");
        } else {
          router.push("/");
        }
      } catch {
        // If auto-login fails, redirect to login page
        router.push("/login");
      }
    }, 1500);
  } catch (err: any) {
    error.value = err.message || "An error occurred during registration";
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