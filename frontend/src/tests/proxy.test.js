const { proxyRequest } = require('../services/proxy');
const axios = require('axios');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

jest.mock('axios');
jest.mock('fs');

const mockSwaggerYml = `
openapi: 3.0.0
info:
  title: "Test API"
  version: "1.0.0"
paths:
  /test:
    post:
      summary: "Test Endpoint"
`;

describe('Proxy Service', () => {
  beforeAll(() => {
    fs.readFileSync.mockReturnValue(mockSwaggerYml);
  });

  test('should load routes from swagger.yml', () => {
    const swaggerFilePath = path.resolve(__dirname, '../pages/swagger.yml');
    const yamlContent = fs.readFileSync(swaggerFilePath, 'utf8');
    const swaggerDoc = yaml.load(yamlContent);
    expect(swaggerDoc).toHaveProperty('paths');
    expect(swaggerDoc.paths).toHaveProperty('/test');
  });

  test('should forward valid POST requests to backend', async () => {
    const mockResponse = { data: { message: 'Success' } };
    axios.post.mockResolvedValue(mockResponse);

    const response = await proxyRequest('/test', { key: 'value' });

    expect(axios.post).toHaveBeenCalledWith(
      `${process.env.REACT_APP_API_URL}/test`,
      { key: 'value' }
    );
    expect(response).toEqual(mockResponse.data);
  });

  test('should throw error for unsupported routes', async () => {
    await expect(proxyRequest('/invalid', { key: 'value' }))
      .rejects
      .toThrow('Invalid or unsupported API path: /invalid');
  });

  test('should handle backend errors gracefully', async () => {
    axios.post.mockRejectedValue(new Error('Network Error'));

    await expect(proxyRequest('/test', { key: 'value' }))
      .rejects
      .toThrow('Error forwarding request to backend: Network Error');
  });
});
