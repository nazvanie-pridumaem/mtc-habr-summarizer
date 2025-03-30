# --- Сборочный этап ---
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# --- Финальный образ с NGINX ---
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Удаляем дефолтный конфиг nginx
RUN rm /etc/nginx/conf.d/default.conf

# Кладём наш простой конфиг
COPY nginx.conf /etc/nginx/conf.d

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
