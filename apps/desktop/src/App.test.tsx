import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/health")) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                name: "Gravity AI",
                version: "0.1.0",
                status: "ok",
                rootDir: "E:\\Users\\Mob\\Nova pasta (2)\\Gravity Assistente",
                tools: 2,
                plugins: 1,
              }),
              { status: 200, headers: { "content-type": "application/json" } },
            ),
          );
        }

        return Promise.resolve(
          new Response(
            JSON.stringify({
              tools: [
                {
                  name: "file.list",
                  description: "List files and directories in a path.",
                  parameters_schema: {},
                  permissions: ["filesystem.read"],
                  risk: "safe",
                  requires_confirmation: false,
                },
              ],
            }),
            { status: 200, headers: { "content-type": "application/json" } },
          ),
        );
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the Gravity AI command center", async () => {
    render(<App />);

    expect(screen.getByText("Gravity AI")).toBeInTheDocument();
    expect(screen.getByText("Command Center")).toBeInTheDocument();
    expect(await screen.findByText("file.list")).toBeInTheDocument();
  });
});

