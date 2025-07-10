export const paths = {
  app: {
    home: {
      path: "/",
      getHref: () => "/",
    },
    chat: {
      path: "/chat",
      getHref: () => "/chat",
    },
  },
} as const;
