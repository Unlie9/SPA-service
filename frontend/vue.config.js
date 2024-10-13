const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
	transpileDependencies: true,

	// Добавляем devServer для проксирования запросов
	devServer: {
		proxy: {
			'/media': {
				target: 'http://localhost:8000', // Укажите адрес вашего Django-сервера
				changeOrigin: true,
			},
		},
	},
})
