import { createBrowserRouter, RouterProvider } from "react-router-dom";

import AppRoot from "./routes/app/root";
import Spinner from "@/components/spinner/spinner";
import { paths } from "@/config/paths";

const createAppRouter = () => {
  return createBrowserRouter([
    {
      path: paths.app.home.path,
      element: <AppRoot />,
      hydrateFallbackElement: <Spinner size="large" />,
      children: [
        {
          path: paths.app.chat.path,
          lazy: async () => {
            const module = await import("./routes/app/chat");
            return { Component: module.default };
          },
        },
      ],
    },
    {
      path: "*",
      lazy: async () => {
        const module = await import("./routes/not-found");
        return { Component: module.default };
      },
    },
  ]);
};

export const AppRouter = () => {
  const router = createAppRouter();
  return <RouterProvider router={router} />;
};
