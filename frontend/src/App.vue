<template>
  <div id="app">
    <CommentList /> <!-- Ваш компонент с комментариями -->
  </div>
</template>

<script>
import CommentList from './views/CommentList.vue';

export default {
  name: 'App',
  components: {
    CommentList
  }
}
</script>

<style>

</style>
