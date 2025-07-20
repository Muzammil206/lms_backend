// Load environment variables FIRST
require('dotenv').config();

// Verify critical environment variables
if (!process.env.EMAIL_HOST || !process.env.DATABASE_URL) {
  console.error('Missing required environment variables');
  process.exit(1);
}




const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const winston = require('winston');
const routes = require('./routes');

console.log('ENV LOADED:', process.env.EMAIL_HOST);

// Initialize Express
const app = express();

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Middleware

app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/', routes);

// Error handling
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).json({
    success: false,
    message: 'Internal Server Error'
  });
});

// Start server
const PORT = process.env.PORT || 5000;
const server = app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
});

// Handle shutdown gracefully
process.on('SIGTERM', () => {
  logger.info('SIGTERM received. Shutting down gracefully');
  server.close(() => {
    logger.info('Server shutdown complete');
    process.exit(0);
  });
});

module.exports = app;
