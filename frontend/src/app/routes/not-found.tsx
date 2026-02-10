import { useEffect } from "react";

const NotFound = () => {
  useEffect(() => {
    document.title = "ページが見つかりません - Tuna Chat";

    return () => {
      document.title = "Tuna Chat";
    };
  }, []);

  return <div>notfound</div>;
};

export default NotFound;
