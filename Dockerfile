# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install pnpm globally, a performant package manager
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml (if you use pnpm and generate one)
# Or package-lock.json for npm, or yarn.lock for yarn
COPY package.json ./
# If you generate a pnpm-lock.yaml, uncomment the next line
# COPY pnpm-lock.yaml ./

# Install app dependencies using pnpm
# If not using pnpm, change to 'npm install' or 'yarn install'
RUN pnpm install --frozen-lockfile

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . .

# Compile TypeScript to JavaScript
RUN pnpm run build

# Make port 3000 available to the world outside this container
# Railway will automatically use the PORT environment variable, but it's good practice to expose it.
EXPOSE 3000

# Define the command to run your app
CMD [ "pnpm", "start" ] 