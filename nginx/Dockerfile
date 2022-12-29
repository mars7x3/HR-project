FROM node:19.0.1-alpine as builder

RUN npm install -g npm@9.1.2

WORKDIR /job-kg_frontEnd
COPY ./job-kg_frontEnd/package*.json ./

RUN npm install --save --legacy-peer-deps

COPY ./job-kg_frontEnd .

RUN npm run build
RUN ls

FROM nginx:alpine

COPY --from=builder /job-kg_frontEnd/build/ usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]