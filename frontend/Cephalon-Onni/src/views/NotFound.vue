<template>
    <div class="not-found">
        <div class="glitch-container">
            <div class="glitch-image-wrapper">
                <img :src="imageSrc" class="glitch-base" alt="404" />
                <img :src="imageSrc" class="glitch ghost ghost-right" alt="" />
                <img
                    :src="imageSrc"
                    class="glitch ghost ghost-top-right"
                    alt=""
                />
                <img :src="imageSrc" class="glitch ghost ghost-left" alt="" />
            </div>

            <div class="overlay">
                <h1 class="title glitch-text" data-text="404 Error">
                    404 Error
                </h1>
            </div>
        </div>

        <p class="subtitle">
            {{ subtitle }}
        </p>
    </div>
</template>

<script lang="ts" setup>
interface Props {
    imageSrc: string;
    subtitle?: string;
}

withDefaults(defineProps<Props>(), {
    subtitle: "The page you are looking for does not exist.",
});
</script>

<style scoped>
.not-found {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #0b0b0b;
    color: white;
    overflow: hidden;
}

.glitch-container {
    position: relative;
    width: 320px;
    height: 320px;
}

.overlay {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
    pointer-events: none;
}

.title {
    font-size: 3rem;
    font-weight: 800;
    text-transform: uppercase;
    position: relative;
    color: #707070;
    text-shadow:
        0 0 2px #fff,
        0 0 5px #fff,
        0 0 10px #fff,
        0 0 15px #fff;
}

.glitch-text::before,
.glitch-text::after {
    content: attr(data-text);
    position: absolute;
    inset: 0;
}

.glitch-text::before {
    color: #ff0055;
    transform: translate(2px, 0);
    animation: glitch-text 1.5s infinite;
}

.glitch-text::after {
    color: #00eaff;
    transform: translate(-2px, 0);
    animation: glitch-text 1.5s infinite reverse;
}

.subtitle {
    margin-top: 1.5rem;
    font-size: 1.1rem;
    opacity: 0.8;
    text-align: center;
    max-width: 400px;
}

.glitch-image-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: visible;
    z-index: 1;
}

.glitch-image-wrapper img {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    object-fit: contain;
    transform: translate(-50%, -50%);
    image-rendering: pixelated;
}

.glitch-base {
    z-index: 2;
}

.ghost {
    z-index: 1;
    opacity: 0;
    mix-blend-mode: screen;
    pointer-events: none;
}
.ghost-right {
    filter: drop-shadow(4px 2px cyan);
    animation: glitch-right 2.6s infinite steps(1);
}

.ghost-top-right {
    filter: drop-shadow(3px -3px magenta);
    animation: glitch-top-right 3.1s infinite steps(1);
}

.ghost-left {
    filter: drop-shadow(-4px 0 red);
    animation: glitch-left 2.3s infinite steps(1);
}

@keyframes glitch-text {
    0% {
        clip-path: inset(0 0 90% 0);
    }
    50% {
        clip-path: inset(40% 0 40% 0);
    }
    100% {
        clip-path: inset(90% 0 0 0);
    }
}

@keyframes glitch-right {
    0% {
        opacity: 0;
        clip-path: inset(0 0 100% 0);
    }
    12% {
        opacity: 0.7;
        clip-path: inset(55% 0 20% 0);
        transform: translate(-50%, -50%) translate(6px, 3px);
    }
    18% {
        opacity: 0;
    }
    100% {
        opacity: 0;
    }
}

@keyframes glitch-top-right {
    0% {
        opacity: 0;
        clip-path: inset(0 0 100% 0);
    }
    20% {
        opacity: 0.6;
        clip-path: inset(10% 0 70% 0);
        transform: translate(-50%, -50%) translate(5px, -5px);
    }
    26% {
        opacity: 0;
    }
    100% {
        opacity: 0;
    }
}

@keyframes glitch-left {
    0% {
        opacity: 0;
        clip-path: inset(0 0 100% 0);
    }
    8% {
        opacity: 0.65;
        clip-path: inset(35% 0 40% 0);
        transform: translate(-50%, -50%) translate(-6px, 1px);
    }
    14% {
        opacity: 0;
    }
    100% {
        opacity: 0;
    }
}
</style>
