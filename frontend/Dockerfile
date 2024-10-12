FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm add global @vue/cli
RUN npm install

COPY . .

EXPOSE 8080

CMD ["npm", "run", "serve"]