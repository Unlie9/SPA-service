<template>
  <div id="app">
    <router-view /> <!-- Здесь будут отображаться компоненты страниц -->
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 50px;
}
</style>
