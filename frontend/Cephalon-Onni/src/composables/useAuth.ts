import { ref, computed } from 'vue'

interface User {
    id: string;
    username: string;
    role: string;
}

const user = ref<User | null>(null)

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
        return user.value && user.value.role === "Administrator";
    })

    const isAuthenticated = computed(() => {
        return user.value !== null;
    })

    return {
        user,
        fetchUser,
        logout,
        isAdmin,
        isAuthenticated
    }
}