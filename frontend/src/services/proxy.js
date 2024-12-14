import yaml from 'js-yaml';
import fs from 'fs';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;
if (!API_BASE_URL) {
  throw new Error('Переменная окружения REACT_APP_API_URL не задана');
}

const swaggerFilePath = path.resolve(__dirname, '../pages/swagger.yml'); // Укажите путь к вашему файлу swagger.yml.

function loadApiRoutes() {
  const fileContent = fs.readFileSync(swaggerFilePath, 'utf8');
  const swaggerDoc = yaml.load(fileContent);
  const paths = swaggerDoc.paths;
  return Object.keys(paths).reduce((acc, route) => {
    acc[route] = paths[route].post ? 'POST' : null;
    return acc;
  }, {});
}

const apiRoutes = loadApiRoutes();

export async function proxyRequest(path, data) {
  if (!apiRoutes[path] || apiRoutes[path] !== 'POST') {
    throw new Error(`Некорректный или неподдерживаемый API путь: ${path}`);
  }

  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await axios.post(url, data);
    return response.data;
  } catch (error) {
    throw new Error(`Ошибка при пересылке запроса на бэкенд: ${error.message}`);
  }
}
