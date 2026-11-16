FROM node:22-alpine

WORKDIR /app

RUN apk add --no-cache python3

COPY backend/package*.json ./

RUN npm install

COPY backend/ ./

COPY config/gerar_config.py /app/gerar_config.py

EXPOSE 3000

CMD ["node", "server.js"]