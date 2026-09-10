FROM node:20-alpine

WORKDIR /app

COPY server/package.json ./server/package.json
RUN cd server && npm install --omit=dev

COPY server ./server
COPY app ./app

ENV PORT=3000
EXPOSE 3000

CMD ["node", "server/server.js"]
