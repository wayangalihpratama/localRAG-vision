FROM node:20-slim

WORKDIR /app

# Install dependencies separately for better caching
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "run", "dev"]
