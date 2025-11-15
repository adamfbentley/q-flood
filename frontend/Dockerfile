# Frontend Dockerfile for Q-flood
FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with forced rebuild of native modules
RUN npm install && npm rebuild rollup

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start dev server with host binding for Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
