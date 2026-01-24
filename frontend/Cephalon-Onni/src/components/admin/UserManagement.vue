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
                                class="btn-danger"
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
                        <button @click="deleteUser" class="btn-danger">
                            Delete User
                        </button>
                        <button @click="cancelDelete" class="btn-secondary">
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
            throw new Error("Failed to fetch users");
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
            throw new Error("Failed to update user role");
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
            throw new Error("Failed to delete user");
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
    color: #e2e8f0;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.panel-header h2 {
    color: #7dd3fc;
    margin: 0;
}

.search-bar {
    flex: 1;
    max-width: 400px;
    margin-left: 2rem;
}

.search-input {
    width: 100%;
    padding: 0.5rem 1rem;
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    color: #e2e8f0;
    font-size: 0.875rem;
}

.search-input:focus {
    outline: none;
    border-color: #0ea5e9;
}

.search-input::placeholder {
    color: #64748b;
}

.loading,
.error,
.no-users {
    text-align: center;
    padding: 2rem;
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
}

.error {
    color: #f87171;
    border-color: #f87171;
}

.users-table {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    overflow: hidden;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #1b2a3a;
}

th {
    background: #0f172a;
    color: #7dd3fc;
    font-weight: 600;
}

tr:last-child td {
    border-bottom: none;
}

.role-select {
    padding: 0.25rem 0.5rem;
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    color: #e2e8f0;
    font-size: 0.875rem;
    cursor: pointer;
}

.role-select:focus {
    outline: none;
    border-color: #0ea5e9;
}

.role-select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.role-select option {
    background: #0f172a;
    color: #e2e8f0;
}

.actions {
    display: flex;
    gap: 0.5rem;
}

.btn-primary,
.btn-secondary,
.btn-danger {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
}

.btn-primary {
    background: #0ea5e9;
    color: white;
}

.btn-primary:hover {
    background: #0284c7;
}

.btn-secondary {
    background: #475569;
    color: white;
}

.btn-secondary:hover {
    background: #334155;
}

.btn-danger {
    background: #dc2626;
    color: white;
}

.btn-danger:hover {
    background: #b91c1c;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.modal {
    background: #08121f;
    border: 1px solid #1b2a3a;
    border-radius: 8px;
    padding: 2rem;
    min-width: 400px;
    max-width: 90%;
    outline: none;
    color: #e2e8f0;
}

.modal h3 {
    color: #7dd3fc;
    margin-top: 0;
    margin-bottom: 1rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #cbd5e1;
}

.form-control {
    width: 100%;
    padding: 0.5rem;
    background: #0f172a;
    border: 1px solid #1b2a3a;
    border-radius: 4px;
    color: #e2e8f0;
}

.form-control:focus {
    outline: none;
    border-color: #0ea5e9;
}

.modal-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
}

.warning {
    color: #fbbf24;
    font-weight: 500;
}
</style>
