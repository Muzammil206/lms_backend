const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, 'prisma');

if (fs.existsSync(dir)) {
  fs.rmSync(dir, { recursive: true, force: true });
  console.log('Successfully removed prisma directory');
} else {
  console.log('Prisma directory does not exist');
}
