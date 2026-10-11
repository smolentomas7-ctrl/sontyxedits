import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { BrowserFrame } from "@/components/ui/BrowserFrame";
import { projects } from "@/content/projects";
import type { Dictionary, Locale } from "@/content/i18n";

export function DemoShowcase({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  return (
    <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {projects.map((project, index) => (
        <Reveal as="li" key={project.slug} delay={index * 60} className="flex">
          <Card as="div" className="group flex w-full flex-col overflow-hidden p-4">
            <BrowserFrame url={`webora.sk${project.href}`}>
              <div className="relative aspect-[16/10] overflow-hidden bg-bg">
                <Image
                  src={project.preview.src}
                  alt={project.preview.alt}
                  fill
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  className="object-cover transition-transform duration-300 ease-out group-hover:scale-[1.03]"
                />
              </div>
            </BrowserFrame>

            <div className="flex flex-1 flex-col gap-2 px-1 pb-1 pt-4">
              <p className="t-small font-medium uppercase tracking-[0.14em] text-accent">
                {project.industry[locale]}
              </p>
              <h3 className="font-[family-name:var(--font-space-grotesk)] text-lg font-medium text-text">
                {project.name}
              </h3>
              <p className="t-small flex-1 text-text-muted">{project.description[locale]}</p>

              <Link
                href={project.href}
                className="mt-2 inline-flex items-center gap-1.5 text-[14px] font-medium text-text transition-colors duration-150 hover:text-accent"
              >
                {dict.common.openDemo}
                <ArrowUpRight aria-hidden="true" strokeWidth={1.5} className="size-4" />
              </Link>
            </div>
          </Card>
        </Reveal>
      ))}
    </ul>
  );
}
