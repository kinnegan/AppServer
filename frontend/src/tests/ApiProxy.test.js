import { render, screen, waitFor } from "@testing-library/react";
import ApiProxy from "../components/ApiProxy";
import yaml from "js-yaml";

jest.mock("js-yaml", () => ({
  load: jest.fn(),
}));

jest.mock("../components/ApiProxy", () => ({
  fetch: jest.fn(),
}));

describe("ApiProxy Component", () => {
  it("renders loading state initially", async () => {
    render(<ApiProxy />);
    expect(screen.getByText(/Loading API configuration/)).toBeInTheDocument();
  });

  it("displays error if swagger.yml fails to load", async () => {
    yaml.load.mockImplementation(() => {
      throw new Error("Failed to load");
    });
    render(<ApiProxy />);
    await waitFor(() =>
      expect(
        screen.getByText(/Failed to load API configuration/)
      ).toBeInTheDocument()
    );
  });

  it("renders proxy server status when swagger.yml is loaded", async () => {
    yaml.load.mockResolvedValue({ paths: { "/test": { post: {} } } });
    render(<ApiProxy />);
    await waitFor(() =>
      expect(
        screen.getByText(/Proxy server is running based on swagger.yml configuration/)
      ).toBeInTheDocument()
    );
  });
});
