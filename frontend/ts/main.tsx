/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from "axios";

import { createRoot } from "react-dom/client";
import { StrictMode } from "react";
import { createInertiaApp } from "@inertiajs/react";

import "../main.css";

const pages = import.meta.glob("./pages/**/*.tsx");

document.addEventListener("DOMContentLoaded", () => {
  axios.defaults.xsrfCookieName = "csrftoken";
  axios.defaults.xsrfHeaderName = "X-CSRFToken";

  createInertiaApp({
    resolve: async (name) => {
      const importer = pages[`./pages/${name}.tsx`] as
        | (() => Promise<{ default: any }>)
        | undefined;
      if (!importer) {
        throw new Error(`Page not found: ${name}`);
      }
      const page = (await importer()).default;
      return page;
    },
    setup({ el, App, props }) {
      createRoot(el).render(
        <StrictMode>
          <App {...props} />
        </StrictMode>
      );
    },
  });
});
