FROM node:20-alpine

WORKDIR /app

# Install git and copy .git for VERSION control
RUN apk add --no-cache git
COPY .git .git

COPY skyegpt-frontend/ .
RUN npm ci


RUN npm run build

# Remove .git directory
RUN rm -rf .git

EXPOSE 5173

CMD ["sh", "-c", "npm run set-env && npm run start"]

