const nodemailer = require('nodemailer');
const winston = require('winston');




console.log('ENV CHECK:', {
  EMAIL_HOST: process.env.EMAIL_HOST,
  EMAIL_PORT: process.env.EMAIL_PORT,
  EMAIL_USER: process.env.EMAIL_USER,
  EMAIL_PASSWORD: process.env.EMAIL_PASSWORD,
  EMAIL_FROM: process.env.EMAIL_FROM,
});


// Validate email configuration
const validateConfig = () => {
  const requiredVars = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_FROM'];
  const missingVars = requiredVars.filter(varName => !process.env[varName]);
  
  if (missingVars.length > 0) {
    winston.error(`Missing email configuration: ${missingVars.join(', ')}`);
    throw new Error('Email configuration incomplete');
  }
};

// Create reusable transporter object
let transporter;
try {
  validateConfig();
  
  transporter = nodemailer.createTransport({
    host: process.env.EMAIL_HOST,
    port: parseInt(process.env.EMAIL_PORT),
    secure: process.env.EMAIL_PORT === '465',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASSWORD
    },
    // Additional settings for better handling
    pool: true,
    maxConnections: 5,
    maxMessages: 100,
    // Timeout settings
    connectionTimeout: 10000, // 10 seconds
    greetingTimeout: 5000,    // 5 seconds
    socketTimeout: 10000     // 10 seconds
  });

  // Verify connection on startup
  transporter.verify()
    .then(() => winston.info('SMTP connection verified'))
    .catch(err => winston.error('SMTP verification failed:', err));

} catch (err) {
  winston.error('Email transport initialization failed:', err);
  throw err;
}

// Send email with retry logic
const sendEmail = async (options, retries = 2) => {
  try {
    if (!transporter) throw new Error('Email transporter not initialized');

    const mailOptions = {
      from: `"LMS System" <${process.env.EMAIL_FROM}>`,
      to: options.email,
      subject: options.subject,
      text: options.message,
      html: options.html || options.message,
      // Add priority header
      headers: { 'X-Priority': '1' }
    };

    await transporter.sendMail(mailOptions);
    winston.info(`Email sent to ${options.email}`);

  } catch (err) {
    winston.error(`Email send failed (${retries} retries left):`, err);
    
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries))); // Exponential backoff
      return sendEmail(options, retries - 1);
    }

    throw new Error(`Failed to send email after multiple attempts: ${err.message}`);
  }
};

module.exports = sendEmail;
