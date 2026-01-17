<template>
  <div class="creative-mode">
    <h1>Creative Mode</h1>
    <p class="subtitle">Unleash your imagination, Tenno.</p>
    
    <div class="empty-canvas">
      <div class="placeholder">
        <p>Your creative space awaits...</p>
        <small>Start building your masterpiece</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.creative-mode h1 {
  color: #a78bfa;
  letter-spacing: 2px;
}

.subtitle {
  opacity: 0.7;
  margin-bottom: 2rem;
}

.empty-canvas {
  background: #0f0f23;
  border: 2px dashed #1e1b4b;
  border-radius: 8px;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2rem;
  transition: all 0.3s ease;
}

.empty-canvas:hover {
  border-color: #6366f1;
  background: #11112b;
}

.placeholder {
  text-align: center;
  color: #6366f1;
  opacity: 0.5;
}

.placeholder p {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.placeholder small {
  font-size: 0.9rem;
  opacity: 0.7;
}
</style>