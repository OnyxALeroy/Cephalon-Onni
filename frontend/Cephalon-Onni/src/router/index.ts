import { createRouter, createWebHistory } from "vue-router";
import ConsoleLayout from "@/layouts/ConsoleLayout.vue";

import Home from "@/views/Home.vue";
import Inventory from "@/views/Inventory.vue";
import Admin from "@/views/Admin.vue";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";
import LootTables from "@/views/Loottables.vue";
import Creative from "@/views/Creative.vue";
import NotFound from "@/views/NotFound.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: ConsoleLayout,
      children: [
        { path: "", component: Home },
        { path: "inventory", component: Inventory },
        { path: "loottables", component: LootTables },
        { path: "creative", component: Creative },
        { path: "admin", component: Admin },
      ],
    },

    { path: "/login", component: Login },
    { path: "/register", component: Register },

    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFound,
      props: {
        imageSrc: "/images/404.png",
        subtitle:
          "You should not try to escape my gaze, Tenno. This is MY domain.",
      },
    },
  ],
});
export default router;
