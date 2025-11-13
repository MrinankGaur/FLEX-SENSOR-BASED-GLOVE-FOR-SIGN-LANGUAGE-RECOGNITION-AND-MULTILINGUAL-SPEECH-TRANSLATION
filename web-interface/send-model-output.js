/**
 * Example script to send model output to the web application (Node.js version).
 * 
 * Usage:
 *   node send-model-output.js "Hello, this is a test message"
 * 
 * Or use it in your model script:
 *   const sendModelOutput = require('./send-model-output.js');
 *   const modelOutput = "Hello world";
 *   sendModelOutput(modelOutput);
 */

async function sendModelOutput(text, baseUrl = 'http://localhost:3000') {
  /**
   * Send model output to the web application.
   * 
   * @param {string} text - The text output from your model
   * @param {string} baseUrl - The base URL of your Next.js application
   * @returns {Promise<Object|null>} - Response data or null on error
   */
  const url = `${baseUrl}/api/model-output`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(`✓ Successfully sent: ${text}`);
    return data;
  } catch (error) {
    console.error(`✗ Error sending output: ${error.message}`);
    return null;
  }
}

// If run directly from command line
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node send-model-output.js <text>');
    console.log("Example: node send-model-output.js 'Hello, this is a test message'");
    process.exit(1);
  }

  const text = args.join(' ');
  sendModelOutput(text);
}

module.exports = sendModelOutput;


