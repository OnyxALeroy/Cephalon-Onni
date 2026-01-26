import { ref, computed } from 'vue'

interface User {
    id: string;
    username: string;
    role: string;
}

const user = ref<User | null>(null)
const isInitialized = ref(false)

export function useAuth() {
    async function fetchUser() {
        try {
            const res = await fetch("/api/auth/me", { credentials: "include" });

            if (res.ok) {
                user.value = await res.json();
            } else {
                user.value = null;
            }
        } catch (error) {
            user.value = null;
        } finally {
            isInitialized.value = true;
        }
    }

    async function login(email: string, password: string) {
        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                await fetchUser();
                return await response.json();
            } else {
                throw new Error("Login failed");
            }
        } catch (error) {
            await fetchUser();
            throw error;
        }
    }

    async function register(username: string, email: string, password: string) {
        try {
            const response = await fetch("/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ username, email, password }),
            });

            if (response.ok) {
                await fetchUser();
                return await response.json();
            } else {
                throw new Error("Registration failed");
            }
        } catch (error) {
            await fetchUser();
            throw error;
        }
    }

    async function logout() {
        try {
            await fetch("/api/auth/logout", { 
                method: "POST", 
                credentials: "include" 
            });
            user.value = null;
            window.location.href = "/";
        } catch (error) {
            console.error("Logout failed:", error);
        }
    }

    const isAdmin = computed(() => {
        return user.value && (user.value.role === "Administrator" || user.value.role === "administrator" || user.value.role === "admin");
    })

    const isAuthenticated = computed(() => {
        return user.value !== null;
    })

    return {
        user,
        fetchUser,
        login,
        register,
        logout,
        isAdmin,
        isAuthenticated,
        isInitialized
    }
}