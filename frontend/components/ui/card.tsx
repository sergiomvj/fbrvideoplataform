import { type HTMLAttributes, forwardRef } from "react";

type CardProps = HTMLAttributes<HTMLDivElement>;

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className = "", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={[
          "rounded-xl border border-gray-200 bg-white shadow-sm",
          className,
        ].join(" ")}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";
Card.displayName = "Card";

const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className = "", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={["flex flex-col space-y-1.5 p-6", className].join(" ")}
        {...props}
      />
    );
  }
);
CardHeader.displayName = "CardHeader";
CardHeader.displayName = "CardHeader";

const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className = "", ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={["font-semibold leading-none tracking-tight", className].join(" ")}
        {...props}
      />
    );
  }
);
CardTitle.displayName = "CardTitle";
CardTitle.displayName = "CardTitle";

const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className = "", ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={["text-sm text-gray-500", className].join(" ")}
        {...props}
      />
    );
  }
);
CardDescription.displayName = "CardDescription";
CardDescription.displayName = "CardDescription";

const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className = "", ...props }, ref) => {
    return (
      <div ref={ref} className={["p-6 pt-0", className].join(" ")} {...props} />
    );
  }
);
CardContent.displayName = "CardContent";
CardContent.displayName = "CardContent";

const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className = "", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={["flex items-center p-6 pt-0", className].join(" ")}
        {...props}
      />
    );
  }
);
CardFooter.displayName = "CardFooter";
CardFooter.displayName = "CardFooter";

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  type CardProps,
};
