import { DemoBar, DEMO_BAR_HEIGHT, type DemoKind } from "./DemoBar";

/**
 * Wraps a demo so the fixed Webora bar never overlaps the demo's own header.
 * The inline padding-top is what pushes the demo down by exactly the bar
 * height; each demo's own sticky header then offsets from the same number.
 */
export function DemoShell({
  kind,
  children,
  className,
}: {
  kind: DemoKind;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <>
      <DemoBar kind={kind} />
      <div className={className} style={{ paddingTop: DEMO_BAR_HEIGHT }}>
        {children}
      </div>
    </>
  );
}
