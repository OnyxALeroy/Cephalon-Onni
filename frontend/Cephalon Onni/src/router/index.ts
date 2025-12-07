import { createRouter, createWebHistory } from "vue-router";
import ConsoleLayout from "@/layouts/ConsoleLayout.vue";

import Home from "@/views/Home.vue";
import Inventory from "@/views/Inventory.vue";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: ConsoleLayout,
      children: [
        { path: "", component: Home },
        { path: "inventory", component: Inventory },
      ],
    },

    { path: "/login", component: Login },
    { path: "/register", component: Register },
  ],
});

export default router;
