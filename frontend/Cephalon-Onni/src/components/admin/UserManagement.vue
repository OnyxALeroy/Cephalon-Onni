<template>
    <div class="tab-panel">
        <div class="panel-header">
            <h2>User Management</h2>
            <div class="search-bar">
                <input 
                    v-model="searchQuery" 
                    type="text" 
                    placeholder="Search users..." 
                    class="search-input"
                />
            </div>
        </div>

        <div v-if="loading" class="loading">Loading users...</div>

        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else class="users-table">
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in filteredUsers" :key="user.id">
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>
                            <select 
                                v-model="user.role" 
                                @change="updateUserRole(user)"
                                :disabled="isCurrentUser(user.id)"
                                class="role-select"
                            >
                                <option value="Tenno">Tenno</option>
                                <option value="Traveller">Traveller</option>
                                <option value="Administrator">Administrator</option>
                            </select>
                        </td>
                        <td class="actions">
                            <button
                                @click="confirmDelete(user)"
                                class="btn btn-danger btn-sm"
                                :disabled="isCurrentUser(user.id)"
                            >
                                Delete
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div v-if="filteredUsers.length === 0" class="no-users">
                {{ searchQuery ? 'No users found matching your search' : 'No users found' }}
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <Teleport to="body">
            <div v-if="deletingUser" class="modal-overlay" @click="cancelDelete">
                <div 
                    class="modal" 
                    @click.stop 
                    @keydown.enter="deleteUser"
                    tabindex="-1"
                    ref="modalRef"
                >
                    <h3>Confirm Delete</h3>
                    <p>
                        Are you sure you want to delete user
                        <strong>{{ deletingUser.username }}</strong
                        >?
                    </p>
                    <p class="warning">This action cannot be undone.</p>

                    <div class="modal-actions">
                        <button @click="deleteUser" class="btn btn-danger">
                            Delete User
                        </button>
                        <button @click="cancelDelete" class="btn btn-secondary">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useAuth } from "@/composables/useAuth";

interface User {
    id: string;
    username: string;
    email: string;
    role: string;
}

const { user: currentUser } = useAuth();

const users = ref<User[]>([]);
const loading = ref(true);
const error = ref("");
const deletingUser = ref<User | null>(null);
const searchQuery = ref("");
const modalRef = ref<HTMLElement | null>(null);

const isCurrentUser = (userId: string) => {
    return currentUser.value?.id === userId;
};

const filteredUsers = computed(() => users.value);

const fetchUsers = async () => {
    try {
        const url = searchQuery.value 
            ? `/api/admin/users?search=${encodeURIComponent(searchQuery.value)}`
            : "/api/admin/users";
            
        const response = await fetch(url, {
            credentials: "include",
        });
        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error((data && data.detail) || "Failed to fetch users");
        }
        users.value = await response.json();
    } catch (err) {
        error.value = err instanceof Error ? err.message : "An error occurred";
    } finally {
        loading.value = false;
    }
};

const updateUserRole = async (user: User) => {
    try {
        const response = await fetch(
            `/api/admin/users/${user.id}/role`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ role: user.role }),
                credentials: "include",
            },
        );

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error((data && data.detail) || "Failed to update user role");
        }
    } catch (err) {
        error.value =
            err instanceof Error ? err.message : "Failed to update user role";
        // Revert the change on error
        const originalUser = users.value.find(u => u.id === user.id);
        if (originalUser) {
            user.role = originalUser.role;
        }
    }
};

const confirmDelete = (user: User) => {
    deletingUser.value = user;
};

const cancelDelete = () => {
    deletingUser.value = null;
};

const deleteUser = async () => {
    if (!deletingUser.value) return;

    try {
        const response = await fetch(
            `/api/admin/users/${deletingUser.value.id}`,
            {
                method: "DELETE",
                credentials: "include",
            },
        );

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error((data && data.detail) || "Failed to delete user");
        }

        // Remove user from local data
        users.value = users.value.filter(
            (u) => u.id !== deletingUser.value!.id,
        );
        cancelDelete();
    } catch (err) {
        error.value =
            err instanceof Error ? err.message : "Failed to delete user";
    }
};



// Watch search query changes and refetch
watch(searchQuery, () => {
    fetchUsers();
});

// Watch for delete modal opening and focus it
watch(deletingUser, (newValue) => {
    if (newValue) {
        nextTick(() => {
            if (modalRef.value) {
                modalRef.value.focus();
            }
        });
    }
});

onMounted(() => {
    fetchUsers();
});
</script>

<style scoped>
.tab-panel {
    color: var(--text-heading);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
}

.panel-header h2 {
    color: var(--accent-subtle);
    margin: 0;
}

.search-bar {
    flex: 1;
    max-width: 400px;
    margin-left: var(--space-8);
}

.search-input {
    width: 100%;
    padding: var(--space-2) var(--space-4);
    background: var(--bg-elevated);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
    color: var(--text-heading);
    font-size: var(--text-md);
}

.search-input:focus {
    outline: none;
    border-color: var(--accent-hover);
}

.search-input::placeholder {
    color: var(--text-muted);
}

.loading,
.error,
.no-users {
    text-align: center;
    padding: var(--space-8);
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
}

.error {
    color: var(--error-text);
    border-color: var(--error-text);
}

.users-table {
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
    overflow: hidden;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: var(--space-3);
    text-align: left;
    border-bottom: 1px solid var(--border-primary);
}

th {
    background: var(--bg-elevated);
    color: var(--accent-subtle);
    font-weight: 600;
}

tr:last-child td {
    border-bottom: none;
}

.role-select {
    padding: var(--space-1) var(--space-2);
    background: var(--bg-elevated);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
    color: var(--text-heading);
    font-size: var(--text-md);
    cursor: pointer;
}

.role-select:focus {
    outline: none;
    border-color: var(--accent-hover);
}

.role-select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.role-select option {
    background: var(--bg-elevated);
    color: var(--text-heading);
}

.actions {
    display: flex;
    gap: var(--space-2);
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.modal {
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: var(--space-8);
    min-width: 400px;
    max-width: 90%;
    outline: none;
    color: var(--text-heading);
}

.modal h3 {
    color: var(--accent-subtle);
    margin-top: 0;
    margin-bottom: var(--space-4);
}

.modal-actions {
    display: flex;
    gap: var(--space-2);
    justify-content: flex-end;
    margin-top: var(--space-6);
}

.warning {
    color: var(--warning-text);
    font-weight: 500;
}
</style>
