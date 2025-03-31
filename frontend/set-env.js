// frontend/set-env.js
const fs = require('fs');
const path = require('path');

const dataSourceApiUrl = process.env.DATA_SOURCE_API_URL || 'http://localhost:8003';
const dataSinkApiUrl = process.env.DATA_SINK_API_URL || 'http://localhost:8002';

const envFilePath = path.resolve(__dirname, 'src/environments/environment.ts');

let envFileContent = fs.readFileSync(envFilePath, 'utf8');

envFileContent = envFileContent.replace('${DATA_SOURCE_API_URL}', dataSourceApiUrl);
envFileContent = envFileContent.replace('${DATA_SINK_API_URL}', dataSinkApiUrl);

fs.writeFileSync(envFilePath, envFileContent);

console.log(`- dataSourceApiUrl: ${dataSourceApiUrl}`);
console.log(`- dataSinkApiUrl: ${dataSinkApiUrl}`);
