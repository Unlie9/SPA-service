<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style src="@/assets/global.css"></style>

<style scoped>

.app-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
  position: relative;
  height: 100%;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(8px);
  z-index: 1;
}

.router-view {
  z-index: 2;
  position: relative;
  animation: fadeIn 0.8s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .app-container {
    background: linear-gradient(135deg, #74ebd5 0%, #6cace4 100%);
  }

  .overlay {
    background: rgba(0, 0, 0, 0.15);
  }
}
</style>
