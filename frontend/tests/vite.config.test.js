import assert from "node:assert/strict";
import test from "node:test";

import config from "../../vite.config.js";

test("Vite serves development assets under Django's STATIC_URL", () => {
  assert.equal(config.base, "/static/");
});
