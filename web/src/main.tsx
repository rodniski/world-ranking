import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import "./index.css";
import App from "./App.tsx";

// `VITE_CONVEX_URL` so existe depois de `bun run dev` rodar `convex dev` com
// login. Enquanto nao houver deployment, o cliente fica como `undefined` e a
// landing renderiza normal — qualquer query Convex que venhamos a usar
// vai precisar guardar nesse fallback.
const convexUrl = import.meta.env.VITE_CONVEX_URL as string | undefined;
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {convex ? (
      <ConvexProvider client={convex}>
        <App />
      </ConvexProvider>
    ) : (
      <App />
    )}
  </StrictMode>,
);
