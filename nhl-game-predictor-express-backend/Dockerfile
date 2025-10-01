FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 8002

CMD ["npm", "start"]
