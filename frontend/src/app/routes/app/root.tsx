import { Outlet } from "react-router-dom";
import { Layout } from "@/components/layout/layout";

const AppRoot = () => {
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

export default AppRoot;
