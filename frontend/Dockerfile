FROM node:20-alpine

WORKDIR /app

# When Docker Compose builds with context ./frontend, copy files from context root
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

