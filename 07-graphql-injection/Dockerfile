FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

# Initialize the database during build
ARG FLAG=FLAG_PLACEHOLDER
ENV FLAG=${FLAG}
RUN node init-db.js

# Make database directory and file read-only
RUN chmod 444 /app/data/challenge.db && \
    chmod 555 /app/data

EXPOSE 5000

CMD ["npm", "start"]