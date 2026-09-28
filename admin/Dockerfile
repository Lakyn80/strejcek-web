# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git

COPY package*.json ./
COPY scripts ./scripts
COPY --from=cz-accounting-module / ./.accounting-ui/cz-accounting-module
RUN npm ci --ignore-scripts

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
