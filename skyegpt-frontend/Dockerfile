FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 5173

# We are using DOCKER-compose to run the app in development mode so we dont need to run the dev server here.
# CMD ["npm", "run", "dev"]