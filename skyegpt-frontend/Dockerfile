FROM node:20-alpine
WORKDIR /app
# Build argument
ARG NEXT_PUBLIC_SKYEGPT_BACKEND_HOST
# Set as environment variable for Next.js build
ENV NEXT_PUBLIC_SKYEGPT_BACKEND_HOST=$NEXT_PUBLIC_SKYEGPT_BACKEND_HOST
COPY . .
RUN npm ci
RUN npm run build
EXPOSE 5173

CMD ["npm", "run", "start"]