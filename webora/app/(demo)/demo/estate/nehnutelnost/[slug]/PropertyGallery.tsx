"use client";

import { useState } from "react";
import Image from "next/image";
import { Lightbox, type LightboxItem } from "@/components/ui/Lightbox";
import type { ImageSlot } from "@/config/images";

export function PropertyGallery({
  images,
  title,
}: {
  images: ImageSlot[];
  title: string;
}) {
  const [active, setActive] = useState(0);
  const [lightbox, setLightbox] = useState<number | null>(null);

  const main = images[active] ?? images[0];

  const items: LightboxItem[] = images.map((image) => ({
    src: image.src,
    width: image.width,
    height: image.height,
    alt: image.alt,
    title,
  }));

  return (
    <>
      <button
        type="button"
        onClick={() => setLightbox(active)}
        aria-label={`Zväčšiť fotografiu: ${main.alt}`}
        className="block w-full overflow-hidden rounded-xl"
      >
        <Image
          key={main.src}
          src={main.src}
          width={main.width}
          height={main.height}
          alt={main.alt}
          priority
          sizes="(max-width: 1240px) 100vw, 1240px"
          className="aspect-[3/2] w-full object-cover"
        />
      </button>

      {images.length > 1 ? (
        <ul className="mt-3 grid grid-cols-5 gap-3">
          {images.map((image, index) => (
            <li key={image.src}>
              <button
                type="button"
                onClick={() => setActive(index)}
                aria-label={`Zobraziť fotografiu ${index + 1} z ${images.length}`}
                aria-current={index === active}
                className="block w-full overflow-hidden rounded-lg border-2 transition-colors duration-150"
                style={{ borderColor: index === active ? "#17457A" : "transparent" }}
              >
                <Image
                  src={image.src}
                  width={image.width}
                  height={image.height}
                  alt=""
                  loading="lazy"
                  sizes="180px"
                  className="aspect-[3/2] w-full object-cover"
                />
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      <Lightbox
        items={items}
        index={lightbox}
        onClose={() => setLightbox(null)}
        onIndexChange={setLightbox}
        label={`Fotogaléria: ${title}`}
        counterWord="z"
        closeLabel="Zavrieť"
        prevLabel="Predchádzajúca"
        nextLabel="Ďalšia"
      />
    </>
  );
}
