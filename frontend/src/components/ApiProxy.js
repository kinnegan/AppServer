import React, { useEffect, useState } from "react";
import yaml from "js-yaml";

const ApiProxy = () => {
  const [swaggerConfig, setSwaggerConfig] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSwaggerConfig = async () => {
      try {
        const response = await fetch("/swagger.yml");
        const yamlText = await response.text();
        const config = yaml.load(yamlText);
        setSwaggerConfig(config);
      } catch (err) {
        console.error("Error loading swagger.yml:", err);
        setError("Failed to load API configuration.");
      }
    };

    fetchSwaggerConfig();
  }, []);

  useEffect(() => {
    if (swaggerConfig) {
      const startProxyServer = () => {
        const apiPaths = Object.keys(swaggerConfig.paths);

        apiPaths.forEach((path) => {
          const methods = Object.keys(swaggerConfig.paths[path]);
          methods.forEach((method) => {
            if (method.toLowerCase() === "post") {
              setupRoute(path);
            }
          });
        });
      };

      const setupRoute = (path) => {
        const express = require("express");
        const app = express();
        app.use(express.json());

        app.post(`/api${path}`, async (req, res) => {
          try {
            const backendResponse = await fetch(`http://backend-url${path}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(req.body),
            });

            const responseData = await backendResponse.json();
            res.status(backendResponse.status).json(responseData);
          } catch (err) {
            console.error(`Error forwarding request for ${path}:`, err);
            res.status(500).json({ error: "Failed to forward request to backend." });
          }
        });

        app.listen(3001, () => {
          console.log(`Proxy route set up for POST /api${path}`);
        });
      };

      startProxyServer();
    }
  }, [swaggerConfig]);

  return (
    <div>
      <h2>API Proxy Server</h2>
      {error && (
        <div style={{ color: "red" }}>
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}
      {!swaggerConfig && <p>Loading API configuration...</p>}
      {swaggerConfig && <p>Proxy server is running based on swagger.yml configuration.</p>}
    </div>
  );
};

export default ApiProxy;
