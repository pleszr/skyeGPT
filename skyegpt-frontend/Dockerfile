FROM node:20-alpine
WORKDIR /app

COPY . .
RUN npm ci
RUN npm run build
EXPOSE 5173


CMD ["sh", "-c", "npm run set-env && npm run start"]

