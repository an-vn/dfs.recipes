FROM node:22-alpine AS build

WORKDIR /app

COPY package.json ./
COPY package.lock ./

RUN yarn install --frozen-lockfile # Or npm ci

# Copy the rest of the application files
COPY . .

# Build the Webpack assets
RUN yarn build # Or npm run build

# Stage 2: Serve the assets with Nginx
FROM nginx:alpine

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built Webpack assets from the build stage to Nginx's web root
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for Nginx
EXPOSE 80

