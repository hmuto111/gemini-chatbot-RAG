import { Link } from "react-router-dom";

type CustomLinkProps = {
  href?: string;
  children?: React.ReactNode;
  className?: string;
  title?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
};

export const CustomLink = ({ href, children, ...rest }: CustomLinkProps) => {
  // hrefがない場合
  if (!href) {
    return <span {...rest}>{children}</span>;
  }

  // 注釈リンク（内部アンカー）
  if (href.startsWith("#")) {
    return (
      <a
        href={href}
        onClick={(e) => {
          e.preventDefault();
          const id = href.substring(1);
          const element = document.getElementById(id);
          if (element) {
            element.scrollIntoView({ behavior: "smooth" });
          }
        }}
        {...rest}
      >
        {children}
      </a>
    );
  }

  // 内部リンク
  if (href.startsWith("/")) {
    return (
      <Link to={href} {...rest}>
        {children}
      </Link>
    );
  }

  // 外部リンク
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" {...rest}>
      {children}
    </a>
  );
};
