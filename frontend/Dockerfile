FROM node:22

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Обновляем npm (если нужно)
RUN npm install -g npm@10.9.2

# Устанавливаем все зависимости
RUN npm install

# Копируем остальные файлы проекта
COPY . .

# Собираем проект
RUN npm run build

# Открываем порт
EXPOSE 3500

# Запускаем приложение
CMD ["npm", "start"]
